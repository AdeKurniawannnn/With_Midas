# Usage Examples and Advanced Patterns

## Natural Language to Advanced Search Conversion

- **Input**: "CEO Jakarta fintech"
  **Constructed Query**: `site:linkedin.com/in "Jakarta" CEO fintech OR "financial technology" -recruiter -hr`
  **Target**: C-level executives in Jakarta's financial technology sector

- **Input**: "CTO Bandung cloud computing startup"
  **Constructed Query**: `site:linkedin.com/in Bandung CTO "cloud computing" OR AWS OR Azure startup -recruiter -hr`
  **Target**: Technology leadership in Bandung's cloud computing startup ecosystem

- **Input**: "AI Director Indonesia enterprise"
  **Constructed Query**: `site:linkedin.com/in Indonesia Director AI OR "artificial intelligence" enterprise -recruiter -hr`
  **Target**: AI-focused leadership across Indonesian enterprise companies

- **Input**: "CFO Medan banking multinational"
  **Constructed Query**: `site:linkedin.com/in Medan CFO banking OR "financial services" multinational -recruiter -hr`
  **Target**: Financial leadership in Medan's multinational banking sector

- **Input**: "VP Engineering Bali e-commerce digital transformation"
  **Constructed Query**: `site:linkedin.com/in Bali "VP Engineering" OR "Engineering Director" "e-commerce" OR ecommerce "digital transformation" -recruiter -hr`
  **Target**: Engineering leadership in Bali's e-commerce transformation sector

## Advanced Boolean Logic Examples

- **Multiple locations**: `site:linkedin.com/in ("Jakarta" OR "Surabaya") CEO fintech -recruiter -hr`
- **Technology combos**: `site:linkedin.com/in Indonesia CTO "cloud computing" AND AI -recruiter -hr`
- **Industry exclusions**: `site:linkedin.com/in Indonesia Director technology -manufacturing -recruiter -hr`

## Temporal Targeting

- **Recent activity**: `site:linkedin.com/in Indonesia CEO 2024 "cloud transformation" -recruiter -hr`
- **Fresh content**: `site:linkedin.com/in Jakarta CTO posted shared AI -recruiter -hr`

## Company Size Targeting

- **Enterprise focus**: `site:linkedin.com/in Indonesia CIO multinational corporation "cloud migration" -recruiter -hr`
- **Startup focus**: `site:linkedin.com/in Indonesia CTO founder startup "venture capital" -recruiter -hr`

## Technology-Specific Patterns

- **Cloud expertise**: `site:linkedin.com/in Indonesia (AWS OR Azure OR "Google Cloud") "certified" OR "architect" -recruiter -hr`
- **AI/ML specialization**: `site:linkedin.com/in Indonesia ("machine learning" OR "deep learning" OR "neural networks") researcher OR scientist -recruiter -hr`