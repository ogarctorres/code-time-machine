# 🕰️ Code Time Machine

> Veja a evolução da complexidade de um arquivo Python ao longo de toda sua história.

O **Code Time Machine** viaja pelo histórico completo de commits de um arquivo
específico dentro de um repositório público do GitHub, calculando métricas reais
de qualidade de código (complexidade ciclomática, número de funções, linhas de
código) em cada ponto do tempo — e mostra isso como um gráfico de evolução.

Não é só "ver o diff". É assistir um arquivo nascer, crescer e (às vezes) degradar,
com números reais em cada etapa.

## Por que isso importa

Todo dev já ouviu falar de um arquivo "que ninguém quer mexer" por ser complexo
demais. Mas raramente alguém consegue apontar **quando** e **por que** aquilo
começou a piorar. Esta ferramenta transforma essa intuição em dado visual.

## Como funciona

1. Você cola a URL de um repositório público e o caminho de um arquivo Python.
2. O backend clona o histórico completo e lista todos os commits que alteraram
   esse arquivo especificamente (`git log --follow`).
3. Para uma amostra desses commits, o sistema recupera o conteúdo exato do
   arquivo naquele momento (`git show hash:caminho`) e calcula métricas com
   a biblioteca **radon**.
4. O resultado vira um gráfico de linha mostrando a evolução da complexidade
   média e do número de funções ao longo dos anos.

## Stack

- **Backend:** FastAPI (Python) — histórico de git, cálculo de complexidade via `radon`
- **Frontend:** Next.js 14 + TypeScript + Recharts — gráfico de evolução

## Rodando localmente

### Backend
\`\`\`bash
cd backend
python -m venv venv
# Windows:
venv\\Scripts\\Activate.ps1
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
\`\`\`

### Frontend
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

Acesse `http://localhost:3000`.

## Limitações conhecidas

- Suporta apenas arquivos **Python (.py)**, já que o `radon` é específico dessa linguagem.
- Para não processar centenas de commits (o que seria lento), o sistema faz uma
  **amostragem** do histórico em vez de analisar cada commit individualmente.
- Repositórios com histórico muito longo podem levar alguns segundos para clonar.

## Roadmap

- [ ] Suporte a outras linguagens (JS/TS via `escomplex` ou similar)
- [ ] Destacar automaticamente "pontos de inflexão" (commits que pioraram muito a complexidade)
- [ ] Cache de análises já feitas
- [ ] Modo comparação: dois arquivos lado a lado

## Autor

Feito por [ogarctorres](https://github.com/ogarctorres)