import express, { Request, Response } from "express"
import { logger } from "./logger/index.js"

const app = express()
app.use(express.json())

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY
const ANTHROPIC_BASE_URL = "https://api.anthropic.com"
const HEDGE_COUNT = Number(process.env.HEDGE_COUNT) || 2

interface RequestOptions {
  id: string
  method: string
  url: string
  body: any
  headers: any
  stream: boolean
}

type MakeRequestReturn = {
  response: globalThis.Response; // Prevent conflict with express Response
  reader?: ReadableStreamDefaultReader<Uint8Array>;
  decoder?: TextDecoder;
  data?: any;
}

async function makeRequest({
  id,
  method,
  url,
  body,
  headers,
  stream,
}: RequestOptions): Promise<MakeRequestReturn> {
  const startTime = Date.now()
  try {
    const response = await fetch(url, {
      method,
      body: JSON.stringify(body),
      headers,
    })
    
    const fetchTimeMS = Date.now() - startTime

    if (stream) {
      const reader = response.body!.getReader()
      const decoder = new TextDecoder("utf-8")
      logger.info({ id, fetchTime: fetchTimeMS, stream: true }, "makeRequest completed")
      return { response, reader, decoder }
    } else {
      const data = await response.json()
      const totalTime = Date.now() - startTime
      logger.info({ id, fetchTime: fetchTimeMS, totalTime, stream: false }, "makeRequest completed")
      return { response, data }
    }
  } catch (error) {
    const errorTime = Date.now() - startTime
    logger.error({ id, error, errorTime }, "Error in makeRequest")
    throw error
  }
}

app.all("/v1/*", async (req: Request, res: Response) => {
  const path = req.params[0]
  const url = `${ANTHROPIC_BASE_URL}/v1/${path}`
  const body = req.body
  const isStreaming = body.stream || false

  const headers = {
    ...req.headers,
    "x-api-key": ANTHROPIC_API_KEY,
  }

  delete headers.host

  const startTime = Date.now()

  try {
    const id = crypto.randomUUID()

    const result = await Promise.race(Array.from({ length: HEDGE_COUNT }, () => makeRequest({
      id,
      method: req.method,
      url,
      body,
      headers,
      stream: isStreaming,
    })))

    logger.info({
      id,
      time_taken: Date.now() - startTime,
      is_streaming: isStreaming,
      path,
    },
      "request race finished"
    )

    if (isStreaming) {
      while (true) {
        const { value, done } = await result.reader!.read()
        if (done) break
        const decodedValue = result.decoder!.decode(value)

        logger.debug(`Server-Sent Event: ${decodedValue}`)

        res.write(decodedValue)
      }
      res.end()
    } else {
      const headers = new Headers(result.response.headers)
      headers.delete("content-encoding")

      headers.forEach((value, key) => {
        res.setHeader(key, value)
      })

      res.status(result.response.status).send(result.data)
    }
  } catch (error) {
    logger.error({ error }, "Error in proxy")
    res.status(500).json({ error: "Internal Server Error" })
  }
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => {
  logger.info(`Server is running on port ${PORT}`)
})

export default app
