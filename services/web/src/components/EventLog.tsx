import { useEffect, useMemo, useState } from 'react';

type EventItem = {
  id: number;
  name: string | null;
  event_class: 'ALARM' | 'DEVIATION' | 'EVENT' | string;
  event_state: 'ACTIVE' | 'CLEARED' | string;
  message: string;
  created_at: string | null;
  cleared_at: string | null;
};

type TelemetryItem = {
  conveyor_id: number;
  carcass_count: number;
  created_at: string | null;
};

type ConveyorItem = {
  id: number;
  name: string;
};

type StateFilter = 'ALL' | 'ACTIVE' | 'CLEARED';

const CLASSES = ['ALARM', 'DEVIATION', 'EVENT'] as const;

function formatDateTime(value: string | null): string {
  if (!value) {
    return '—';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }

  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(
    date.getHours(),
  )}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function formatTime(value: string | null): string {
  if (!value) {
    return '—';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }

  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function buildPoints(data: TelemetryItem[]): string {
  if (data.length === 0) {
    return '';
  }

  const width = 520;
  const height = 170;
  const maxY = Math.max(...data.map((item) => item.carcass_count), 1);

  return data
    .map((item, index) => {
      const x = data.length === 1 ? 0 : (index / (data.length - 1)) * width;
      const y = height - (item.carcass_count / maxY) * height;
      return `${x},${y}`;
    })
    .join(' ');
}

function TelemetryChart({ title, data }: { title: string; data: TelemetryItem[] }) {
  const points = buildPoints(data);

  return (
    <article className="telemetry-chart">
      <h3 className="telemetry-chart__title">{title}</h3>
      <svg className="telemetry-chart__svg" viewBox="0 0 520 190" role="img" aria-label={title}>
        <line x1="0" y1="170" x2="520" y2="170" stroke="#bdbdbd" strokeWidth="1" />
        <line x1="0" y1="0" x2="0" y2="170" stroke="#bdbdbd" strokeWidth="1" />
        {points ? <polyline fill="none" stroke="#2962ff" strokeWidth="2" points={points} /> : null}
        {data.length > 0 ? (
          <text x="515" y="186" textAnchor="end" fontSize="11" fill="#616161">
            {formatTime(data[data.length - 1].created_at)}
          </text>
        ) : null}
      </svg>
    </article>
  );
}

export default function EventLog() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [selectedClasses, setSelectedClasses] = useState<Record<string, boolean>>({
    ALARM: true,
    DEVIATION: true,
    EVENT: true,
  });
  const [stateFilter, setStateFilter] = useState<StateFilter>('ALL');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [telemetry, setTelemetry] = useState<TelemetryItem[]>([]);
  const [conveyors, setConveyors] = useState<ConveyorItem[]>([]);

  useEffect(() => {
    let isMounted = true;

    const loadEvents = async () => {
      try {
        const response = await fetch('/api/events');
        if (!response.ok) {
          return;
        }

        const data = (await response.json()) as EventItem[];
        if (isMounted) {
          setEvents(data);
        }
      } catch (_error) {
        // noop
      }
    };

    const loadTelemetry = async () => {
      try {
        const [telemetryResponse, conveyorsResponse] = await Promise.all([
          fetch('/api/telemetry'),
          fetch('/api/conveyors'),
        ]);

        if (telemetryResponse.ok && conveyorsResponse.ok && isMounted) {
          const telemetryData = (await telemetryResponse.json()) as TelemetryItem[];
          const conveyorsData = (await conveyorsResponse.json()) as ConveyorItem[];
          setTelemetry(telemetryData);
          setConveyors(conveyorsData);
        }
      } catch (_error) {
        // noop
      }
    };

    loadEvents();
    loadTelemetry();
    const timerId = window.setInterval(() => {
      loadEvents();
      loadTelemetry();
    }, 10000);

    return () => {
      isMounted = false;
      window.clearInterval(timerId);
    };
  }, []);

  const filteredEvents = useMemo(
    () =>
      events.filter((event) => {
        if (!selectedClasses[event.event_class]) {
          return false;
        }

        if (stateFilter === 'ACTIVE') {
          return event.event_state === 'ACTIVE';
        }

        if (stateFilter === 'CLEARED') {
          return event.event_state === 'CLEARED';
        }

        return event.event_state === 'ACTIVE' || event.event_state === 'CLEARED';
      }),
    [events, selectedClasses, stateFilter],
  );

  const telemetryByConveyor = useMemo(() => {
    const grouped = new Map<number, TelemetryItem[]>();
    telemetry.forEach((item) => {
      const bucket = grouped.get(item.conveyor_id) ?? [];
      bucket.push(item);
      grouped.set(item.conveyor_id, bucket);
    });
    return grouped;
  }, [telemetry]);

  return (
    <section className="event-log" aria-label="Журнал событий">
      <div className="event-log__actions">
        <button type="button" className="event-log__graph-btn" onClick={() => setIsModalOpen(true)}>
          Графики
        </button>
      </div>
      <h2 className="event-log__title">ЖУРНАЛ СОБЫТИЙ</h2>
      <div className="event-log__filters">
        <div className="event-log__filter-group">
          {CLASSES.map((eventClass) => (
            <label key={eventClass} className="event-log__checkbox">
              <input
                type="checkbox"
                checked={selectedClasses[eventClass]}
                onChange={(event) =>
                  setSelectedClasses((prev) => ({ ...prev, [eventClass]: event.target.checked }))
                }
              />
              {eventClass}
            </label>
          ))}
        </div>
        <div className="event-log__filter-group">
          <button
            type="button"
            className={stateFilter === 'ALL' ? 'event-log__filter-btn event-log__filter-btn--active' : 'event-log__filter-btn'}
            onClick={() => setStateFilter('ALL')}
          >
            Все
          </button>
          <button
            type="button"
            className={stateFilter === 'ACTIVE' ? 'event-log__filter-btn event-log__filter-btn--active' : 'event-log__filter-btn'}
            onClick={() => setStateFilter('ACTIVE')}
          >
            Активные
          </button>
          <button
            type="button"
            className={stateFilter === 'CLEARED' ? 'event-log__filter-btn event-log__filter-btn--active' : 'event-log__filter-btn'}
            onClick={() => setStateFilter('CLEARED')}
          >
            Архивные
          </button>
        </div>
      </div>
      <div className="event-log__table-wrap">
        <table className="event-log__table">
          <thead>
            <tr>
              <th>Время появления</th>
              <th>Время снятия</th>
              <th>Класс</th>
              <th>Описание</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.map((event) => (
              <tr
                key={event.id}
                className={`event-log__row event-log__row--${event.event_class.toLowerCase()} ${
                  event.event_state === 'ACTIVE' ? 'event-log__row--active' : 'event-log__row--cleared'
                }`}
              >
                <td>{formatDateTime(event.created_at)}</td>
                <td>{formatDateTime(event.cleared_at)}</td>
                <td>{event.event_class}</td>
                <td>{event.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isModalOpen ? (
        <div className="telemetry-modal" role="dialog" aria-modal="true" aria-label="Графики количества туш">
          <div className="telemetry-modal__panel">
            <div className="telemetry-modal__header">
              <h2>Графики количества туш</h2>
              <button type="button" onClick={() => setIsModalOpen(false)}>
                Закрыть
              </button>
            </div>
            <div className="telemetry-modal__content">
              {conveyors.map((conveyor) => (
                <TelemetryChart
                  key={conveyor.id}
                  title={conveyor.name}
                  data={telemetryByConveyor.get(conveyor.id) ?? []}
                />
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
