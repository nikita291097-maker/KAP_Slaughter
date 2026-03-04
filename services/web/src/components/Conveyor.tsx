export type ConveyorStatus = 'running' | 'stopped' | 'error' | 'warning';

type ConveyorProps = {
  name: string;
  status: ConveyorStatus;
  load: number;
};

const STATUS_META: Record<ConveyorStatus, { belt: string; indicator: string; labelClass: string }> = {
  running: { belt: '#00c853', indicator: '#00c853', labelClass: 'conveyor-label--light' },
  stopped: { belt: '#5c5c5c', indicator: '#5c5c5c', labelClass: 'conveyor-label--muted' },
  error: { belt: '#ff3b30', indicator: '#ff3b30', labelClass: 'conveyor-label--light' },
  warning: { belt: '#ff9800', indicator: '#ff9800', labelClass: 'conveyor-label--light' }
};

export default function Conveyor({ name, status, load }: ConveyorProps) {
  const meta = STATUS_META[status];
  const rollerClass = `roller${status === 'running' ? ' roller--running' : ''}`;
  const indicatorClass = `conveyor-indicator${status === 'error' ? ' conveyor-indicator--error' : ''}`;

  return (
    <article className="conveyor-card" aria-label={name}>
      <svg
        className="conveyor-svg"
        viewBox="0 0 360 130"
        role="img"
        aria-label={`${name}, статус ${status}, загрузка ${load}%`}
      >
        <rect className="conveyor-track" x="30" y="50" width="300" height="30" rx="15" fill="#2d2d2d" />
        <rect className="conveyor-belt" x="36" y="56" width="288" height="18" rx="9" fill={meta.belt} />

        {[70, 140, 210, 280].map((x) => (
          <g key={x} transform={`translate(${x} 65)`}>
            <circle className={rollerClass} r="13" fill="#1a1a1a" />
            <circle className={rollerClass} r="5" fill="#7a7a7a" />
          </g>
        ))}

        <circle className={indicatorClass} cx="40" cy="106" r="7" fill={meta.indicator} />
        <text x="30" y="24" className={`conveyor-label ${meta.labelClass}`}>
          {name}
        </text>
        <text x="235" y="115" className={`conveyor-load ${meta.labelClass}`}>
          Загрузка: {load}%
        </text>
      </svg>
    </article>
  );
}
