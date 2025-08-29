# Makefile for meama-simulation project

.PHONY: help install dev clean fill-customers

help:
	@echo "Available commands:"
	@echo "  make gen-example-customers  - Generate example customers data"
	@echo "  make clean           - Clean cache and temp files"
	@echo "  make install         - Install dependencies"
	@echo "  make gen-product-catalog - Generate product catalog"

# Install dependencies
install:
	source venv/bin/activate && pip install -r requirements.txt

# Fill example customers - your main script
gen-example-customers:
	source venv/bin/activate && python src/scripts/generate_example_customers.py

gen-product-catalog:
	source venv/bin/activate && python src/scripts/generate_product_catalog.py

# Clean up Python cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleanup complete!"
