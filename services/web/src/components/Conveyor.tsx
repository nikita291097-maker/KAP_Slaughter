export type ConveyorStatus = 'RUNNING' | 'STOPPED' | 'ERROR' | 'WARNING' | 'MAINTENANCE';

type ConveyorProps = {
  name: string;
  status: ConveyorStatus;
  carcassCount: number;
  updatedAt: string | null;
};

const STATUS_META: Record<ConveyorStatus, { belt: string; indicator: string; labelClass: string }> = {
  RUNNING: { belt: '#00c853', indicator: '#00c853', labelClass: 'conveyor-label--dark' },
  STOPPED: { belt: '#9e9e9e', indicator: '#9e9e9e', labelClass: 'conveyor-label--dark' },
  ERROR: { belt: '#ff3b30', indicator: '#ff3b30', labelClass: 'conveyor-label--dark' },
  WARNING: { belt: '#ff9800', indicator: '#ff9800', labelClass: 'conveyor-label--dark' },
  MAINTENANCE: { belt: '#1e88e5', indicator: '#1e88e5', labelClass: 'conveyor-label--dark' }
};

function formatUpdatedAt(updatedAt: string | null): string {
  if (!updatedAt) return 'нет данных';
  const date = new Date(updatedAt);
  if (Number.isNaN(date.getTime())) return updatedAt;
  return date.toLocaleString('sv-SE').replace('T', ' ');
}

export default function Conveyor({ name, status, carcassCount, updatedAt }: ConveyorProps) {
  const meta = STATUS_META[status];
  const rollerGroupClass = `roller${status === 'RUNNING' ? ' roller--running' : ''}`;
  const indicatorClass = `conveyor-indicator${status === 'ERROR' ? ' conveyor-indicator--error' : ''}`;

  // Зубья шестерни (8 штук по окружности)
  const teethAngles = [0, 45, 90, 135, 180, 225, 270, 315];
  const teeth = teethAngles.map((angle) => {
    const rad = (angle * Math.PI) / 180;
    const cx = 13 * Math.cos(rad);
    const cy = 13 * Math.sin(rad);
    return (
      <circle
        key={angle}
        cx={cx}
        cy={cy}
        r="2.5"
        fill={meta.indicator}
        stroke="none"
      />
    );
  });

  return (
    <article className="conveyor-card" aria-label={name}>
      <svg className="conveyor-svg" viewBox="0 0 360 130" role="img" aria-label={`${name}, статус ${status}`}>
        <rect className="conveyor-track" x="30" y="50" width="300" height="30" rx="15" fill="#dadce0" />
        <rect className="conveyor-belt" x="36" y="56" width="288" height="18" rx="9" fill={meta.belt} />

        {[70, 140, 210, 280].map((x) => (
          // Внешняя группа – только позиция
          <g key={x} transform={`translate(${x} 65)`}>
            {/* Внутренняя группа – вращение (если RUNNING) */}
            <g className={rollerGroupClass}>
              <circle r="13" fill="#2d2d2d" stroke="#1a1a1a" strokeWidth="1" />
              <circle r="5" fill="#f0f0f0" stroke="#808080" strokeWidth="0.5" />
              {teeth}
            </g>
          </g>
        ))}

        <circle className={indicatorClass} cx="40" cy="106" r="7" fill={meta.indicator} />
        <text x="30" y="24" className={`conveyor-label ${meta.labelClass}`}>
          {name}
        </text>
        <text x="175" y="115" className={`conveyor-load ${meta.labelClass}`}>
          Кол-во туш на линии: {carcassCount}
        </text>
      </svg>
      <p className="conveyor-updated">Обновлено: {formatUpdatedAt(updatedAt)}</p>
    </article>
  );
}