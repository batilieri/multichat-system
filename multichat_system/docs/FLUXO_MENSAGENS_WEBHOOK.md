# Fluxo de Mensagens via Webhook no MultiChat

Este documento explica como as mensagens enviadas e recebidas aparecem no sistema MultiChat, desde o recebimento do webhook até o armazenamento no banco de dados, e como diferenciá-las.

---

## 1. Fluxograma do Processo

```mermaid
flowchart TD
    A[Recebe Webhook] --> B{event == 'messages.upsert'}
    B -- Sim --> C[Extrai message_key]
    C --> D{fromMe}
    D -- True --> E[Salva como enviada (from_me=True)]
    D -- False --> F[Salva como recebida (from_me=False)]
```

---

## 2. Como os dados aparecem

Quando o sistema recebe um webhook de mensagem, ele processa o JSON e salva cada mensagem com o campo `from_me`:

- **Mensagens enviadas por você (o sistema):**
  - `from_me: true`
- **Mensagens recebidas de outros contatos:**
  - `from_me: false`

Exemplo de registro salvo:
```json
{
  "id": 123,
  "chat": 7,
  "remetente": "Elizeu Batiliere",
  "content": "Te amo",
  "timestamp": "2025-07-18T12:08:35.706676-03:00",
  "type": "texto",
  "from_me": true
}
```

---

## 3. Como filtrar/encontrar no backend

- **Mensagens enviadas:**
  ```python
  Mensagem.objects.filter(from_me=True)
  ```
- **Mensagens recebidas:**
  ```python
  Mensagem.objects.filter(from_me=False)
  ```

---

## 4. Como exibir no frontend

No frontend, use o campo `from_me` (ou `fromMe`) para decidir o lado do balão:
- `from_me: true` → balão à direita (mensagem enviada)
- `from_me: false` → balão à esquerda (mensagem recebida)

---

## 5. Resumo

- O campo **from_me** diferencia mensagens enviadas e recebidas em todo o fluxo.
- Basta filtrar ou usar esse campo para separar e exibir corretamente. 