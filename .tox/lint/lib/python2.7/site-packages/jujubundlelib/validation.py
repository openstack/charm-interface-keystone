# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.

from __future__ import unicode_literals

import models
import pyutils
import references
from typeutils import (
    isdict,
    islist,
    isstring,
)


# Define accepted constraint types.
_CONSTRAINTS = (
    'arch',
    'container',
    'cpu',
    'cpu-cores',
    'cpu-power',
    'instance-type',
    'mem',
    'networks',
    'root-disk',
    'spaces',
    'tags',
)


def validate(bundle):
    """Validate a bundle object and all of its components.

    The bundle must be passed as a YAML decoded object.

    Return a list of bundle errors, or an empty list if the bundle is valid.
    """
    errors = []
    add_error = errors.append

    # Check that the bundle sections are well formed.
    series, services, machines, relations = _validate_sections(
        bundle, add_error)
    # If there are errors already, there is no point in proceeding with the
    # validation process.
    if errors:
        return errors

    # Validate each individual section.
    _validate_series(series, 'bundle', add_error)
    _validate_services(services, machines, add_error)
    _validate_machines(machines, add_error)
    _validate_relations(relations, services, add_error)

    # Return all the collected errors.
    return errors


def _validate_sections(bundle, add_error):
    """Check that the base bundle sections are valid.

    The bundle argument is a YAML decoded bundle content.

    A bundle is composed of series, services, machines and relations.
    Only the services section is mandatory.

    Use the given add_error callable to register validation error.
    Return the four sections
    """
    # Check that the bundle itself is well formed.
    if not isdict(bundle):
        add_error('bundle does not appear to be a bundle')
        return None, None, None, None
    # Validate the services section.
    services = bundle.get('services', {})
    if not services:
        add_error('bundle does not define any services')
    elif not isdict(services):
        add_error('services spec does not appear to be well-formed')
    # Validate the machines section.
    machines = bundle.get('machines')
    if machines is not None:
        if isdict(machines):
            try:
                machines = dict((int(k), v) for k, v in machines.items())
            except (TypeError, ValueError):
                add_error('machines spec identifiers must be digits')
        else:
            add_error('machines spec does not appear to be well-formed')
    # Validate the relations section.
    relations = bundle.get('relations')
    if (relations is not None) and (not islist(relations)):
        add_error('relations spec does not appear to be well-formed')
    return bundle.get('series'), services, machines, relations


def _validate_series(series, label, add_error):
    """Check that the given series is valid.

    Use the given label (e.g. "machine X" or just "bundle") to describe
    possible errors.
    Use the given add_error callable to register validation error.
    """
    if series is None:
        return
    if not isstring(series):
        add_error('{} series must be a string, found {}'.format(label, series))
        return
    if series == 'bundle':
        add_error('{} series must specify a charm series'.format(label))
        return
    if not references.valid_series(series):
        add_error('{} has invalid series {}'.format(label, series))


def _validate_services(services, machines, add_error):
    """Validate each service within the bundle.

    Receive the services and machines sections of the bundle.
    Use the given add_error callable to register validation error.
    """
    machine_ids = set()

    for service_name, service in services.items():
        if not isstring(service_name):
            add_error('service name {} must be a string'.format(service_name))
        if service.get('expose') not in (True, False, None):
            add_error(
                'invalid expose value for service {}'.format(service_name))
        # Validate and retrieve the service charm URL and number of units.
        charm = _validate_charm(service.get('charm'), service_name, add_error)
        num_units = _validate_num_units(
            service.get('num_units'), service_name, add_error)
        # Validate service constraints and storage constraints.
        label = 'service {}'.format(service_name)
        _validate_constraints(service.get('constraints'), label, add_error)
        _validate_storage(service.get('storage'), service_name, add_error)
        # Validate service options and annotations.
        _validate_options(service.get('options'), service_name, add_error)
        _validate_annotations(service.get('annotations'), label, add_error)
        # Retrieve and validate the service units placement.
        placements = service.get('to', [])
        if not islist(placements):
            placements = [placements]
        if (num_units is not None) and (len(placements) > num_units):
            add_error(
                'too many units placed for service {}'.format(service_name))
        for placement in placements:
            machine_id = _validate_placement(
                placement, services, machines, charm, add_error)
            machine_ids.add(machine_id)

    if machines is not None:
        # Notify unused machines.
        unused = set(machines).difference(machine_ids)
        for machine_id in unused:
            add_error(
                'machine {} not referred to by a placement directive'
                ''.format(machine_id))


def _validate_charm(url, service_name, add_error):
    """Validate the given charm URL.

    Use the given service name to describe possible errors.
    Use the given add_error callable to register validation error.

    If the URL is valid, return the corresponding charm reference object.
    Return None otherwise.
    """
    if url is None:
        add_error('no charm specified for service {}'.format(service_name))
        return None
    if not isstring(url):
        add_error(
            'invalid charm specified for service {}: {}'
            ''.format(service_name, url))
        return None
    if not url.strip():
        add_error('empty charm specified for service {}'.format(service_name))
        return None
    try:
        charm = references.Reference.from_string(url)
    except ValueError as e:
        msg = pyutils.exception_string(e)
        add_error(
            'invalid charm specified for service {}: {}'
            ''.format(service_name, msg))
        return None
    if charm.is_local():
        add_error(
            'local charms not allowed for service {}: {}'
            ''.format(service_name, charm))
        return None
    if charm.is_bundle():
        add_error(
            'bundle cannot be used as charm for service {}: {}'
            ''.format(service_name, charm))
        return None
    return charm


def _validate_num_units(num_units, service_name, add_error):
    """Check that the given num_units is valid.

    Use the given service name to describe possible errors.
    Use the given add_error callable to register validation error.

    If no errors are encountered, return the number of units as an integer.
    Return None otherwise.
    """
    if num_units is None:
        # This should be a subordinate charm.
        return 0
    try:
        num_units = int(num_units)
    except (TypeError, ValueError):
        add_error(
            'num_units for service {} must be a digit'.format(service_name))
        return
    if num_units < 0:
        add_error(
            'num_units {} for service {} must be a positive digit'
            ''.format(num_units, service_name))
        return
    return num_units


def _validate_constraints(constraints, label, add_error):
    """Validate the given service or machine constraints.

    Use the given label (e.g. "machine X" or "service Y") to describe
    possible errors.
    Use the given add_error callable to register validation error.
    """
    if constraints is None:
        return
    msg = '{} has invalid constraints {}'.format(label, constraints)
    if not isstring(constraints):
        add_error(msg)
        return
    sep = ',' if ',' in constraints else None
    for constraint in constraints.split(sep):
        try:
            key, value = constraint.split('=')
        except (TypeError, ValueError):
            add_error(msg)
            return
        if key not in _CONSTRAINTS:
            add_error(msg)


def _validate_storage(storage, service_name, add_error):
    """Lazily validate the storage constraints, ensuring that they are a dict.

    Use the given add_error callable to register validation error.
    """
    if storage is None:
        return
    if not isdict(storage):
        msg = 'service {} has invalid storage constraints {}'.format(
            service_name, storage)
        add_error(msg)


def _validate_options(options, service_name, add_error):
    """Lazily validate the options, ensuring that they are a dict.

    Use the given add_error callable to register validation error.
    """
    if options is None:
        return
    if not isdict(options):
        add_error('service {} has malformed options'.format(service_name))


def _validate_annotations(annotations, label, add_error):
    """Check that the given service or machine annotations are valid.

    Use the given label (e.g. "machine X" or "service Y") to describe
    possible errors.
    Use the given add_error callable to register validation error.
    """
    if annotations is None:
        return
    if not isdict(annotations):
        add_error('{} has invalid annotations {}'.format(label, annotations))
        return
    # Check that all the annotations keys are strings.
    if not all(map(isstring, annotations)):
        add_error(
            '{} has invalid annotations: keys must be strings'.format(label))


def _validate_placement(placement, services, machines, charm, add_error):
    """Validate a placement directive against other services.

    Receive the placement (possibly as a string), the services and machines
    bundle sections, the corresponding charm (or None if invalid) and the
    add_error callable used to register validation errors.

    If applicable, also validate the placement of other machines within the
    bundle.

    Note that some of the logic within this differs between legacy and
    version 4 bundles.

    Return the placement machine id if applicable, None otherwise.
    """
    if not isstring(placement):
        add_error(
            'invalid placement {}: placement must be a string'
            ''.format(placement))
        return
    is_legacy_bundle = machines is None
    try:
        if is_legacy_bundle:
            # This is a v3 legacy bundle.
            unit_placement = models.parse_v3_unit_placement(placement)
            # This is a v4 new style bundle.
        else:
            unit_placement = models.parse_v4_unit_placement(placement)
    except ValueError as e:
        add_error(pyutils.exception_string(e))
        return
    if unit_placement.service:
        service = services.get(unit_placement.service)
        if service is None:
            add_error(
                'placement {} refers to non-existent service {}'
                ''.format(placement, unit_placement.service))
            return
        if unit_placement.unit is not None:
            try:
                num_units = int(service['num_units'])
            except (TypeError, ValueError):
                # This will be notified when validating the service itself.
                pass
            else:
                if int(unit_placement.unit) + 1 > num_units:
                    add_error(
                        'placement {} specifies a unit greater than the units '
                        'in service {}'
                        ''.format(placement, unit_placement.service))
    elif (
        unit_placement.machine and
        not is_legacy_bundle and
        (unit_placement.machine != 'new')
    ):
        machine_id = int(unit_placement.machine)
        # A machine can be included in machines but its value can be None.
        # This is so that we are compatible with go-style YAML unmarshaling.
        if machine_id not in machines:
            add_error(
                'placement {} refers to a non-existent machine {}'
                ''.format(placement, unit_placement.machine))
            return
        machine = machines[machine_id]
        if not isdict(machine):
            # Ignore this error here, as it is emitted while validating the
            # machines section of the bundle.
            machine = {}
        # If the unit is "hulk smashed", then we need to check that the charm
        # and the machine series match.
        if not unit_placement.container_type:
            series = machine.get('series')
            if charm.series and series and charm.series != series:
                # If the machine series is invalid, ignore this check, as an
                # error for the machine will be added elsewhere.
                errors = []
                _validate_series(series, '', errors.append)
                if not errors:
                    add_error(
                        'charm {} cannot be deployed to machine with '
                        'different series {}'.format(charm, series))
        return machine_id


def _validate_machines(machines, add_error):
    """Validate the given machines section.

    Validation includes machines constraints, series and annotations.
    Use the given add_error callable to register validation error.
    """
    if not machines:
        return
    for machine_id, machine in machines.items():
        if machine_id < 0:
            add_error(
                'machine {} has an invalid id, must be positive digit'
                ''.format(machine_id))
        if machine is None:
            continue
        elif not isdict(machine):
            add_error(
                'machine {} does not appear to be well-formed'
                ''.format(machine_id))
            continue
        label = 'machine {}'.format(machine_id)
        _validate_constraints(machine.get('constraints'), label, add_error)
        _validate_series(machine.get('series'), label, add_error)
        _validate_annotations(machine.get('annotations'), label, add_error)


def _validate_relations(relations, services, add_error):
    """Validate relations, ensuring that the endpoints exist.

    Receive the relations and services bundle sections.
    Use the given add_error callable to register validation error.
    """
    if not relations:
        return
    for relation in relations:
        if not islist(relation):
            add_error('relation {} is malformed'.format(relation))
            continue
        relation_str = ' -> '.join('{}'.format(i) for i in relation)
        for endpoint in relation:
            if not isstring(endpoint):
                add_error(
                    'relation {} has malformed endpoint {}'
                    ''.format(relation_str, endpoint))
                continue
            try:
                service, _ = endpoint.split(':')
            except ValueError:
                service = endpoint
            if service not in services:
                add_error(
                    'relation {} endpoint {} refers to a non-existent service '
                    '{}'.format(relation_str, endpoint, service))
