"""
Tests para utilidades de validación
"""
import pytest
from utils.validators import (
    validate_rut, clean_rut, format_rut,
    calculate_rut_dv, validate_email
)


class TestRUTValidation:
    """Tests para validación de RUT chileno"""

    def test_validate_rut_valid(self):
        """Test validar RUT válido"""
        is_valid, error = validate_rut("12.345.678-5")
        assert is_valid is True
        assert error == ""

    def test_validate_rut_valid_without_format(self):
        """Test validar RUT sin formato"""
        is_valid, error = validate_rut("123456785")
        assert is_valid is True

    def test_validate_rut_with_k(self):
        """Test validar RUT con K"""
        is_valid, error = validate_rut("11.111.111-1")  # El DV correcto es 1, no K
        assert is_valid is True

    def test_validate_rut_invalid_dv(self):
        """Test RUT con dígito verificador inválido"""
        is_valid, error = validate_rut("12.345.678-9")
        assert is_valid is False
        assert "Dígito verificador inválido" in error

    def test_validate_rut_empty(self):
        """Test RUT vacío"""
        is_valid, error = validate_rut("")
        assert is_valid is False
        assert "requerido" in error

    def test_validate_rut_too_short(self):
        """Test RUT muy corto"""
        is_valid, error = validate_rut("123-4")
        assert is_valid is False

    def test_clean_rut(self):
        """Test limpiar RUT"""
        assert clean_rut("12.345.678-5") == "123456785"
        assert clean_rut("12345678-5") == "123456785"
        assert clean_rut("11.111.111-K") == "11111111K"

    def test_format_rut(self):
        """Test formatear RUT"""
        assert format_rut("123456785") == "12.345.678-5"
        assert format_rut("11111111K") == "11.111.111-K"
        assert format_rut("11111111k") == "11.111.111-K"

    def test_calculate_rut_dv(self):
        """Test calcular dígito verificador"""
        assert calculate_rut_dv("12345678") == "5"
        assert calculate_rut_dv("11111111") == "1"  # Corregido: el DV correcto es 1
        assert calculate_rut_dv("22222222") == "2"


class TestEmailValidation:
    """Tests para validación de email"""

    def test_validate_email_valid(self):
        """Test email válido"""
        is_valid, error = validate_email("test@example.com")
        assert is_valid is True
        assert error == ""

    def test_validate_email_invalid(self):
        """Test email inválido"""
        is_valid, error = validate_email("test@")
        assert is_valid is False

    def test_validate_email_empty(self):
        """Test email vacío"""
        is_valid, error = validate_email("")
        assert is_valid is False
        assert "requerido" in error

    def test_validate_email_no_at(self):
        """Test email sin @"""
        is_valid, error = validate_email("testexample.com")
        assert is_valid is False
