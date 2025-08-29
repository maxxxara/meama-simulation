# Simulation

## Simulation Overview and Objective

This document outlines an agent-based simulation developed using the **Mesa library** to forecast company revenue during an upcoming promotional campaign. The primary goal of this project is to quantitatively assess the campaign's impact on customer behavior and determine its potential financial benefit.

The model employs a **probabilistic approach**, where each customer is represented as an independent **agent**. These agents make individual decisions on whether to place an order, based on probabilities derived from the historical data provided.

By running this simulation, the project will generate a robust forecast for:

- **Total Revenue:** The expected revenue for the company throughout the campaign period.
- **Campaign Lift:** The projected increase in revenue compared to a standard, non-campaign period.

The ultimate purpose of this simulation is to provide the company with a powerful, data-driven tool to inform its marketing strategy and evaluate the effectiveness of its investments. This approach moves beyond simple estimations, offering a dynamic and nuanced look into the potential outcomes of the campaign.

## Campaign (Raffle) Rules:

### Period:

Start - 2025, 1 September / End - 2025 30 November

### Raffle:

#### Every Week:

- Monday - 1000 GEL
- Tuesday - 1500 GEL
- Wednesday - 2000 GEL
- Thursday - 3000 GEL
- Friday - 3500 GEL

#### One time prizes:

- Final: In 15 October A BMW M4 will be raffled.
- Super Final: In 30 November A CyberTruck will be raffled.

### How to participate:

- When User make any order in meama any store, they will get 1 raffle ticket.
- Tickets (Winners) will be randomly selected.

--

### Customer Data

**Total Customers:** ~52,000

### Customer Information Structure

Each customer record contains:

- **Customer ID** - Unique identifier
- **Email** - Customer email address
- **Historical Spending** - Total value in GEL spent by this customer
- **Average Order Value** - Average spending per order for this customer
- **Total Orders** - Number of orders placed by this customer
- **Historical Purchase Frequency** - Array containing all orders by this customer

### Order Information Structure (Historical Purchase Frequency)

Each order in the purchase frequency array contains:

- **Order ID** - Unique order identifier
- **Total Spent** - Amount spent in GEL for this order
- **Order Date** - When the order was placed
- **Order Lines** - Array of products in this order

### Order Line Structure

Each order line contains:

- **Product Name** - Name of the product
- **Product Price** - Price of the product in GEL
- **Quantity** - Number of units ordered

--

## Previous Campaign Results

Analysis of 2 previous campaigns:

### Campaign 1 Results (New Customers Acquired)

| Post-Campaign Orders                     | Customers                      | % of Total               | Avg. Active Months                           |
| ---------------------------------------- | ------------------------------ | ------------------------ | -------------------------------------------- |
| _(How many extra orders after campaign)_ | _(Number of unique new users)_ | _(Share of total 1,933)_ | _(How long they kept buying after campaign)_ |
| **0** (no repeat)                        | 979                            | **50.7%**                | 0.0                                          |
| **1 order**                              | 439                            | 22.7%                    | 1.0                                          |
| **2 orders**                             | 196                            | 10.1%                    | 1.8                                          |
| **3–4 orders**                           | 189                            | 9.8%                     | 2.6–3.2                                      |
| **5–7 orders**                           | 187                            | 9.7%                     | 3.5–5.0                                      |
| **8+ orders**                            | 32                             | 1.6%                     | 5.0+                                         |

### Campaign 2 Results (New Customers Acquired)

| Post-Campaign Orders                     | Customers                      | % of Total               | Avg. Active Months                           |
| ---------------------------------------- | ------------------------------ | ------------------------ | -------------------------------------------- |
| _(How many extra orders after campaign)_ | _(Number of unique new users)_ | _(Share of total 1,933)_ | _(How long they kept buying after campaign)_ |
| **0** (no repeat)                        | 950                            | **53.2%**                | 0.0                                          |
| **1 order**                              | 400                            | 22.4%                    | 1.0                                          |
| **2 orders**                             | 179                            | 10.0%                    | 1.8                                          |
| **3–4 orders**                           | 161                            | 9.0%                     | 2.6–3.2                                      |
| **5–7 orders**                           | 75                             | 4.2%                     | 3.9-4.9                                      |
| **8+ orders**                            | 21                             | 1.2%                     | 5.3–5.7                                      |

---

## Non-Campaign Baseline Behavior

- **Total Customers in Period:** 22,339
- **Average Orders per Customer:** ~6.26
- **Average Revenue per Customer:** ~185.56 GEL
- **Total Orders in Period:** 139,886
- **Total Revenue in Period:** 4,145,401.19 GEL
