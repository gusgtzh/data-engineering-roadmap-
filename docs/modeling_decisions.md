# Modeling Decisions

## Fact Table
- Grain defined at transaction level
- Metrics aligned with transaction grain (Total_Cost, Total_Items)

## Bridge Table
- Used to model many-to-many relationship between transactions and products
- Grain: transaction-product

## Design Choices
- Avoided storing product lists in fact table (denormalization risk)
- Prevented metric inflation by separating fact and bridge