'use client'

import { useState, useRef, useEffect } from 'react'
import { Loader2, MessageSquare } from 'lucide-react'
import Markdown from 'react-markdown'
import { API_BASE_URL } from '@/config/constants'

type Message = {
	id: number
	sender: 'user' | 'bot'
	text: string
}

export default function Chatbot() {
	const [messages, setMessages] = useState<Message[]>([])
	const [input, setInput] = useState('')
	const [loading, setLoading] = useState(false)
	const [sample, setSample] = useState<string | null>(null)
	const containerRef = useRef<HTMLDivElement | null>(null)
	const nextId = useRef(1)

	const SAMPLE_PROMPTS = [
		'Should I sell Onion now or wait?',
		'Explain recent volatility for Tomato',
		'What factors influence Wheat prices in Maharashtra?',
	]

	useEffect(() => {
		const id = nextId.current++
		setMessages([
			{
				id,
				sender: 'bot',
				text: 'Hi — I can answer market and pricing questions. Try a sample prompt or ask anything.',
			},
		])
	}, [])

	useEffect(() => {
		if (!containerRef.current) return
		containerRef.current.scrollTop = containerRef.current.scrollHeight
	}, [messages, loading])

	const sendQuery = async (q: string) => {
		if (!q.trim()) return
		const userId = nextId.current++
		setMessages((m) => [...m, { id: userId, sender: 'user', text: q }])
		setInput('')
		setLoading(true)
		try {
			const res = await fetch(`${API_BASE_URL}/agent_query`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ query: q }),
			})
			const json = await res.json()
			const botId = nextId.current++
			const botText = json.response || 'No answer available.'
			setMessages((m) => [
				...m,
				{ id: botId, sender: 'bot', text: botText },
			])
		} catch (err) {
			const botId = nextId.current++
			setMessages((m) => [
				...m,
				{
					id: botId,
					sender: 'bot',
					text: 'Request failed. Is the backend running?',
				},
			])
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
			<div className="flex items-center gap-3 mb-4">
				<div className="bg-green-100 p-2 rounded-lg">
					<MessageSquare className="w-5 h-5 text-green-600" />
				</div>
				<div>
					<h3 className="text-lg font-semibold">Chat Assistant</h3>
					<p className="text-sm text-gray-500">
						Ask the data lake — try one of these prompts
					</p>
				</div>
			</div>

			<div className="flex flex-wrap gap-2 mb-4">
				{SAMPLE_PROMPTS.map((p) => (
					<button
						key={p}
						onClick={() => {
							setSample(p)
							sendQuery(p)
						}}
						className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-800 px-3 py-1.5 rounded-full cursor-pointer"
					>
						{p}
					</button>
				))}
			</div>

			<div
				ref={containerRef}
				className="h-full overflow-y-auto rounded-lg border border-gray-100 p-4 mb-4 bg-white"
			>
				{messages.map((m) => (
					<div
						key={m.id}
						className={`mb-3 flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
					>
						<div
							className={`${m.sender === 'user' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-900'} max-w-[80%] px-4 py-2 rounded-lg`}
						>
							<Markdown>{m.text}</Markdown>
						</div>
					</div>
				))}
				{loading && (
					<div className="flex items-center gap-2 text-sm text-gray-500">
						<Loader2 className="w-4 h-4 animate-spin" /> Thinking...
					</div>
				)}
			</div>

			<div className="flex gap-2">
				<input
					value={input}
					onChange={(e) => setInput(e.target.value)}
					onKeyDown={(e) => {
						if (e.key === 'Enter') sendQuery(input)
					}}
					placeholder="Type your question — e.g. 'Should I sell now?'"
					className="flex-1 p-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-200"
				/>
				<button
					onClick={() => sendQuery(input)}
					disabled={loading}
					className="bg-green-600 text-white px-4 rounded-lg disabled:opacity-60"
				>
					Send
				</button>
			</div>
		</div>
	)
}
