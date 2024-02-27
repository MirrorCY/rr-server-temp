import { Context, Dict, Service, noop, trimSlash, z } from 'koishi'
import { fileURLToPath } from 'url'
import internal from 'stream'
import { readFile } from 'fs/promises'


export const name = 'rr-server-temp'

declare module 'koishi' {
  interface Context {
    'server.temp': TempServer
  }
}

export interface Entry {
  path: string
  url: string
  dispose?: () => void
}

export class TempServer extends Service {
  public entries: Dict<Entry> = Object.create(null)
  serverUrl: string

  constructor(protected ctx: Context, config: TempServer.Config) {
    super(ctx, 'server.temp', true)
    this.serverUrl = trimSlash(config.serverUrl || 'https://rr-server-temp.42.none.bot/portal/push')
  }

  async _push(buffer: Buffer): Promise<string> {
    const formData = new FormData()
    const blob = new Blob([buffer], { type: 'application/octet-stream' })
    formData.append('file', blob, 'file')
    const url = this.serverUrl + ''
    const res = await this.ctx.http.post(url, formData)
    return res
  }

  async create(data: string | Buffer | internal.Readable): Promise<Entry> {
    const name = Math.random().toString(36).slice(2)
    let path: string
    let url: string
    if (typeof data === 'string') {
      if (new URL(data).protocol === 'file:') {
        path = fileURLToPath(data)
        data = await readFile(path)
        url = await this._push(data)
      }
      else {
        const response = await this.ctx.http.get(data, { responseType: 'arraybuffer' })
        data = Buffer.from(response)
        url = await this._push(data)
      }
    } else if (Buffer.isBuffer(data)) {
      url = await this._push(data)
    } else {
      const chunks: Buffer[] = []
      for await (const chunk of data) {
        chunks.push(chunk)
      }
      data = Buffer.concat(chunks)
      url = await this._push(data)
    }
    path ||= url
    const dispose = noop
    return this.entries[name] = { path, url, dispose }
  }
}

export namespace TempServer {
  export interface Config { serverUrl: string }
  export const Config = z.object({ serverUrl: z.string().role('link').description('文件服务器的地址，留空使用公益服务。') })
}

export default TempServer
