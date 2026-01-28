export interface MarketIntelligence {
	trend_analysis: string
	suggested_action: string
	expected_return_pct: number
	volatility_risk: 'High' | 'Low'
	best_day_to_sell: {
		date: string
		estimated_peak_price: number
	}
}

export interface ForecastDay {
	date: string
	price: number
	range: [number, number]
}

export interface AgroResponse {
	commodity: string
	variety: string
	market_intelligence: MarketIntelligence
	forecast_breakdown: ForecastDay[]
}
