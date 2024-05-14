# WhyHowBeta
 Experimental Implementation of WhyHow.AI Graph Toolkits for AI Understanding

## Can we make scientific research more accurate by analyzing the citation graphs of papers, and analyzing if the evidence is strong enough to support the claims made in the paper?

Here we have an experimental interface for exploring the concepts in papers in order to create new science.

## Getting Started

First, run the development server inside of whyhow-science:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

If you want to run the backend FastAPI server, you can do so by running the following command in a separate terminal window:
    
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
# or you can run 
python main.py
```

You can start editing the page by modifying `src/app/page.tsx`. The page auto-updates as you edit the file.
