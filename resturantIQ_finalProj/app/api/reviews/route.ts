import { NextResponse } from 'next/server'
import { readFile } from 'node:fs/promises'
import path from 'node:path'

const csvPath = path.join(process.cwd(), 'data', 'sample_reviews.csv')

function splitCsvLine(line: string) {
  const values: string[] = []
  let current = ''
  let quoted = false
  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    if (char === '"' && line[i + 1] === '"' && quoted) { current += '"'; i++; continue }
    if (char === '"') { quoted = !quoted; continue }
    if (char === ',' && !quoted) { values.push(current.trim()); current = ''; continue }
    current += char
  }
  values.push(current.trim())
  return values
}

function parseCsv(csv: string) {
  const lines = csv.trim().split(/\r?\n/)
  const headers = splitCsvLine(lines.shift() ?? '')
  return lines.map((line, index) => {
    const values = splitCsvLine(line)
    return Object.fromEntries(headers.map((header, i) => [header, values[i] ?? '']))
  }).map((row, index) => ({
    id: row.review_id || `R${String(index + 1).padStart(4, '0')}`,
    date: row.date,
    branch: row.branch,
    cuisine: row.cuisine,
    rating: Number(row.rating) || 0,
    text: row.review_text,
    type: row.dining_type,
    foodQuality: Number(row.food_quality) || 0,
    service: Number(row.service_rating) || 0,
    cleanliness: Number(row.cleanliness_rating) || 0,
    price: Number(row.price_rating) || 0,
    sentiment: Number(row.rating) >= 4 ? 'Positive' : Number(row.rating) <= 2 ? 'Negative' : 'Neutral',
  }))
}

// Simple in-memory cache to avoid re-reading/parsing the CSV on every request.
let cachedReviews: ReturnType<typeof parseCsv> | null = null
let cacheTimestamp = 0
const CACHE_TTL = 1000 * 60 // 1 minute

export async function GET() {
  try {
    if (cachedReviews && Date.now() - cacheTimestamp < CACHE_TTL) {
      return NextResponse.json({ reviews: cachedReviews, source: 'cache' })
    }

    const csv = await readFile(csvPath, 'utf8')
    const parsed = parseCsv(csv)
    cachedReviews = parsed
    cacheTimestamp = Date.now()
    return NextResponse.json({ reviews: parsed, source: 'sample_reviews.csv' })
  } catch (err) {
    console.error('Failed to read/parse reviews CSV:', err)
    return NextResponse.json({ error: 'Review data is unavailable.' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => null)
    if (!body || typeof body !== 'object') return NextResponse.json({ error: 'Invalid JSON body.' }, { status: 400 })

    const text = typeof body.text === 'string' ? body.text.trim() : ''
    if (!text) return NextResponse.json({ error: 'Review text is required.' }, { status: 400 })
    if (text.length > 5000) return NextResponse.json({ error: 'Review text is too long.' }, { status: 400 })

    const lower = text.toLowerCase()
    const negativeWords = ['slow', 'cold', 'dirty', 'rude', 'wrong', 'wait', 'expensive', 'bad']
    const positiveWords = ['great', 'excellent', 'fresh', 'friendly', 'delicious', 'wonderful', 'quick']
    const negative = negativeWords.filter(word => lower.includes(word))
    const positive = positiveWords.filter(word => lower.includes(word))
    const sentiment = negative.length > positive.length ? 'Negative' : positive.length > negative.length ? 'Positive' : 'Neutral'

    // Return small, predictable payload and echo any matched negative signals to support UI highlights.
    return NextResponse.json({ sentiment, score: Math.max(-1, Math.min(1, (positive.length - negative.length) / 3)), signals: { negative, positive } })
  } catch (err) {
    console.error('POST /api/reviews error:', err)
    return NextResponse.json({ error: 'Failed to analyze sentiment.' }, { status: 500 })
  }
}
