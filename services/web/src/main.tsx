import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

const stages = [
  { id: 'hopper', label: 'Бункер', active: false },
  { id: 'line-1', label: 'Конвейер 1', active: true },
  { id: 'line-2', label: 'Конвейер 2', active: false },
  { id: 'cutting', label: 'Разделка', active: false },
  { id: 'packing', label: 'Упаковка', active: false }
] as const;

function App() {
  const blockWidth = 170;
  const blockHeight = 70;
  const gap = 44;
  const startX = 20;
  const startY = 80;
  const svgWidth = startX * 2 + stages.length * blockWidth + (stages.length - 1) * gap;
  const svgHeight = 240;

  return (
    <main className="scada-screen">
      <h1>КАП. УБОЙ.</h1>
      <section className="mnemonic-wrapper" aria-label="Мнемосхема конвейера">
        <svg
          role="img"
          aria-label="Статическая мнемосхема конвейера"
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <marker
              id="arrow"
              markerWidth="12"
              markerHeight="12"
              refX="10"
              refY="6"
              orient="auto"
              markerUnits="strokeWidth"
            >
              <path d="M0,0 L12,6 L0,12 z" fill="#ffffff" />
            </marker>
          </defs>

          {stages.map((stage, index) => {
            const x = startX + index * (blockWidth + gap);
            const y = startY;

            return (
              <g key={stage.id}>
                <rect
                  x={x}
                  y={y}
                  width={blockWidth}
                  height={blockHeight}
                  rx={8}
                  fill={stage.active ? '#00c853' : '#2d2d2d'}
                  stroke="#ffffff"
                  strokeWidth="2"
                />
                <text
                  x={x + blockWidth / 2}
                  y={y + blockHeight / 2}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="#ffffff"
                >
                  {stage.label}
                </text>

                {index < stages.length - 1 && (
                  <line
                    x1={x + blockWidth + 8}
                    y1={y + blockHeight / 2}
                    x2={x + blockWidth + gap - 8}
                    y2={y + blockHeight / 2}
                    stroke="#ffffff"
                    strokeWidth="3"
                    markerEnd="url(#arrow)"
                  />
                )}
              </g>
            );
          })}
        </svg>
      </section>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
