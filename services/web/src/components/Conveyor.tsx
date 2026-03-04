type ConveyorProps = {
  name: string;
  load: number;
};

const BELT_COLOR = '#00c853';

export default function Conveyor({ name, load }: ConveyorProps) {
  return (
    <article className="conveyor-card" aria-label={name}>
      <svg
        className="conveyor-svg"
        viewBox="0 0 360 130"
        role="img"
        aria-label={`${name}, загрузка ${load}%`}
      >
        <rect className="conveyor-track" x="30" y="50" width="300" height="30" rx="15" fill="#2d2d2d" />
        <rect className="conveyor-belt" x="36" y="56" width="288" height="18" rx="9" fill={BELT_COLOR} />

        {[70, 140, 210, 280].map((x) => (
          <g key={x} transform={`translate(${x} 65)`}>
            <circle className="roller" r="13" fill="#1a1a1a" />
            <line x1="0" y1="-10" x2="0" y2="10" stroke="#7a7a7a" strokeWidth="2" />
            <line x1="-10" y1="0" x2="10" y2="0" stroke="#7a7a7a" strokeWidth="2" />
          </g>
        ))}

        <circle cx="320" cy="24" r="7" fill={BELT_COLOR} />
        <text x="30" y="24" className="conveyor-label">
          {name}
        </text>
        <text x="235" y="115" className="conveyor-load">
          Загрузка: {load}%
        </text>
      </svg>
    </article>
  );
}
