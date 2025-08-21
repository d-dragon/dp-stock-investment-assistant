# API tests (REST endpoints)

## Non-stream default:
```console
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"message\":\"Latest news on AAPL\"}"
```
Should return JSON with provider/model/fallback fields.

## Provider override:
```console
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"message\":\"Price of TSLA\",\"provider\":\"grok\"}"
```
If Grok fails (no key) it should fallback and still respond (fallback true).

## Streaming: Use a curl session:
```console
curl -N -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"message\":\"Market overview for AAPL and MSFT\",\"stream\":true}"
```
First event: meta. Then chunk events. Then done + [DONE].

WebSocket: Connect with a SocketIO test client and send: { "message": "Price of AAPL", "provider": "openai" } Expect chat_response containing provider & model.

## Config endpoint:
```console

curl http://localhost:5000/api/config
```
```
Now reflects unified model config.

Let me know if you want a follow-up refactor to expose a public agent.process(query) wrapper.