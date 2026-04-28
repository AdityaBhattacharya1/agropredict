'use client'

import React, { useState, useEffect } from 'react'
import {
	LineChart,
	Line,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	ResponsiveContainer,
	AreaChart,
	Area,
} from 'recharts'
import {
	TrendingUp,
	AlertTriangle,
	Calendar,
	ArrowUpRight,
	Loader2,
	Leaf,
} from 'lucide-react'
import { AgroResponse } from '../../types/agro'
import Chatbot from './Chatbot'
import { API_BASE_URL } from '@/config/constants'
import { COMMODITIES } from '@/config/commodities'

export default function AgroDashboard() {
	const [commodity, setCommodity] = useState(COMMODITIES[0])
	const [data, setData] = useState<AgroResponse | null>(null)
	const [loading, setLoading] = useState(false)

	const handlePredict = async () => {
		setLoading(true)
		try {
			const res = await fetch(`${API_BASE_URL}/predict`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					commodity,
					variety: 'Other',
					days: 15,
				}),
			})
			const result = await res.json()
			setData(result)
		} catch (err) {
			alert('Prediction failed. Ensure backend is running.')
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
			<header className="bg-white border-b border-gray-200">
				<div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
					<div className="flex items-center gap-3 mb-4">
						<div className="bg-green-100 p-2 rounded-lg">
							<Leaf className="w-6 h-6 text-green-600" />
						</div>
						<h1 className="text-3xl font-extrabold tracking-tight text-gray-900">
							AgroPredict{' '}
							<span className="text-green-600">Pro</span>
						</h1>
					</div>
					<p className="text-gray-600 max-w-2xl">
						Advanced market intelligence and price forecasting for
						Indian Mandis. Harnessing Prophet AI to empower farmers
						with actionable "Sell or Hold" signals.
					</p>
				</div>
			</header>

			<main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
				<div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
					<div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
						<div>
							<label className="block mb-2 text-sm font-medium text-gray-700">
								Select Commodity
							</label>
							<select
								className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block w-full p-2.5"
								value={commodity}
								onChange={(e) => setCommodity(e.target.value)}
							>
								{COMMODITIES.map((c, idx) => (
									<option key={`${c}_${idx}`} value={c}>
										{c}
									</option>
								))}
							</select>
						</div>

						<button
							onClick={handlePredict}
							disabled={loading}
							className="text-white bg-green-600 hover:bg-green-700 focus:ring-4 focus:outline-none focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center justify-center gap-2"
						>
							{loading && (
								<Loader2 className="w-4 h-4 animate-spin" />
							)}
							Generate Intelligence
						</button>
					</div>
				</div>

				{data && (
					<div className="space-y-8 animate-in fade-in duration-500">
						<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
							<div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
								<div className="flex items-center justify-between mb-2">
									<p className="text-sm text-gray-500">
										Suggested Action
									</p>
									<TrendingUp className="w-5 h-5 text-green-500" />
								</div>
								<h3 className="text-xl font-bold text-gray-900">
									{data.market_intelligence.suggested_action}
								</h3>
								<p className="text-sm text-green-600 font-medium mt-1">
									{data.market_intelligence.trend_analysis}
								</p>
							</div>

							<div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
								<div className="flex items-center justify-between mb-2">
									<p className="text-sm text-gray-500">
										Expected Return
									</p>
									<ArrowUpRight className="w-5 h-5 text-blue-500" />
								</div>
								<h3 className="text-2xl font-bold">
									{
										data.market_intelligence
											.expected_return_pct
									}
									%
								</h3>
								<p className="text-sm text-gray-500 mt-1">
									Next 15-day window
								</p>
							</div>

							<div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
								<div className="flex items-center justify-between mb-2">
									<p className="text-sm text-gray-500">
										Volatility Risk
									</p>
									<AlertTriangle
										className={`w-5 h-5 ${data.market_intelligence.volatility_risk === 'High' ? 'text-red-500' : 'text-green-500'}`}
									/>
								</div>
								<h3 className="text-2xl font-bold">
									{data.market_intelligence.volatility_risk}
								</h3>
								<p className="text-sm text-gray-500 mt-1">
									Based on price spread
								</p>
							</div>

							<div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
								<div className="flex items-center justify-between mb-2">
									<p className="text-sm text-gray-500">
										Optimal Sell Date
									</p>
									<Calendar className="w-5 h-5 text-purple-500" />
								</div>
								<h3 className="text-xl font-bold text-gray-900">
									{
										data.market_intelligence
											.best_day_to_sell.date
									}
								</h3>
								<p className="text-sm text-purple-600 font-medium mt-1">
									Peak: ₹
									{
										data.market_intelligence
											.best_day_to_sell
											.estimated_peak_price
									}
								</p>
							</div>
						</div>

						<div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
							<h3 className="text-lg font-semibold mb-6">
								15-Day Price Forecast (₹/Quintal)
							</h3>
							<div className="h-[400px] w-full">
								<ResponsiveContainer width="100%" height="100%">
									<AreaChart data={data.forecast_breakdown}>
										<defs>
											<linearGradient
												id="colorPrice"
												x1="0"
												y1="0"
												x2="0"
												y2="1"
											>
												<stop
													offset="5%"
													stopColor="#16a34a"
													stopOpacity={0.1}
												/>
												<stop
													offset="95%"
													stopColor="#16a34a"
													stopOpacity={0}
												/>
											</linearGradient>
										</defs>
										<CartesianGrid
											strokeDasharray="3 3"
											vertical={false}
											stroke="#f3f4f6"
										/>
										<XAxis
											dataKey="date"
											tick={{ fontSize: 12 }}
											tickMargin={10}
										/>
										<YAxis
											tick={{ fontSize: 12 }}
											domain={['auto', 'auto']}
										/>
										<Tooltip
											contentStyle={{
												borderRadius: '8px',
												border: 'none',
												boxShadow:
													'0 4px 6px -1px rgb(0 0 0 / 0.1)',
											}}
										/>
										<Area
											type="monotone"
											dataKey="price"
											stroke="#16a34a"
											strokeWidth={3}
											fillOpacity={1}
											fill="url(#colorPrice)"
										/>
									</AreaChart>
								</ResponsiveContainer>
							</div>
						</div>

						{/* Chat assistant card */}
					</div>
				)}
				{/* <Chatbot /> */}
			</main>
		</div>
	)
}
