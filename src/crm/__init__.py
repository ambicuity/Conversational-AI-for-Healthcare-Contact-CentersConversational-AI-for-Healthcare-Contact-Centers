"""CRM package for customer relationship management."""

from .provider import CRMProvider, SalesforceCRM, CRMFactory

__all__ = ['CRMProvider', 'SalesforceCRM', 'CRMFactory']
