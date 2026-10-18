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

export async function GET() {
  try {
    const csv = await readFile(csvPath, 'utf8')
    return NextResponse.json({ reviews: parseCsv(csv), source: 'sample_reviews.csv' })
  } catch {
    return NextResponse.json({ error: 'Review data is unavailable.' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null)
  if (!body?.text || typeof body.text !== 'string') return NextResponse.json({ error: 'Review text is required.' }, { status: 400 })
  const text = body.text.toLowerCase()
  const negativeWords = ['slow', 'cold', 'dirty', 'rude', 'wrong', 'wait', 'expensive', 'bad']
  const positiveWords = ['great', 'excellent', 'fresh', 'friendly', 'delicious', 'wonderful', 'quick']
  const negative = negativeWords.filter(word => text.includes(word))
  const positive = positiveWords.filter(word => text.includes(word))
  const sentiment = negative.length > positive.length ? 'Negative' : positive.length > negative.length ? 'Positive' : 'Neutral'
  return NextResponse.json({ sentiment, score: Math.max(-1, Math.min(1, (positive.length - negative.length) / 3)), signals: negative })
}
