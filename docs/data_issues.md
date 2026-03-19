# Data Limitations

## Missing Product-Level Metrics
- No quantity per product
- No revenue per product
- Cannot compute product-level sales

## Implications
- Any attempt to calculate revenue per product would be incorrect
- Model enforces grain consistency to prevent invalid metrics

## Known Risks
- Metric inflation when joining fact and bridge