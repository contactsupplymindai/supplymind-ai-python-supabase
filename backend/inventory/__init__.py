"""
Inventory Management Django App

This Django app provides comprehensive REST API endpoints for inventory management
using shared models connected to Supabase database.

Features:
- Product and category management
- Supplier management  
- Multi-warehouse inventory tracking
- Stock movement history
- Automated stock alerts
- Product variants support
- Advanced filtering and search capabilities
- Stock adjustment operations

API Base URL: /api/inventory/

Main Models:
- Product: Core product information
- ProductCategory: Product categorization
- Supplier: Supplier management
- InventoryItem: Stock tracking per warehouse
- Warehouse: Warehouse/location management
- StockMovement: Stock movement history
- ProductVariant: Product variations
- StockAlert: Automated inventory alerts
"""

default_app_config = 'inventory.apps.InventoryConfig'
