from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .models import Device, DeviceModel, InstitutionalUnit, Location, Vendor


class InventoryConsistencyTests(SimpleTestCase):
    def setUp(self):
        self.oti = InstitutionalUnit(id=1, name="OTI")
        self.faculty = InstitutionalUnit(id=2, name="Facultad")
        self.oti_room = Location(id=1, name="Sala OTI", unit=self.oti)
        self.faculty_room = Location(
            id=2,
            name="Sala de facultad",
            unit=self.faculty,
        )
        self.cisco = Vendor(id=1, name="Cisco")
        self.other_vendor = Vendor(id=2, name="Otro fabricante")
        self.switch_model = DeviceModel(
            id=1,
            vendor=self.cisco,
            name="Modelo de switch",
            device_type=DeviceModel.DeviceType.SWITCH,
        )

    def test_location_parent_must_belong_to_same_unit(self):
        location = Location(
            name="Rack",
            unit=self.oti,
            parent=self.faculty_room,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "La ubicación superior debe pertenecer a la misma unidad institucional.",
        ):
            location.clean()

    def test_device_location_must_belong_to_device_unit(self):
        device = Device(
            name="Switch",
            unit=self.oti,
            location=self.faculty_room,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "La ubicación debe pertenecer a la misma unidad que el dispositivo.",
        ):
            device.clean()

    def test_device_model_must_match_vendor(self):
        device = Device(
            name="Switch",
            unit=self.oti,
            location=self.oti_room,
            vendor=self.other_vendor,
            model=self.switch_model,
            device_type=DeviceModel.DeviceType.SWITCH,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "El modelo seleccionado no pertenece al fabricante indicado.",
        ):
            device.clean()

    def test_device_type_must_match_model_type(self):
        device = Device(
            name="Switch",
            unit=self.oti,
            location=self.oti_room,
            vendor=self.cisco,
            model=self.switch_model,
            device_type=DeviceModel.DeviceType.ROUTER,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "El tipo del dispositivo debe coincidir con el tipo de su modelo.",
        ):
            device.clean()
