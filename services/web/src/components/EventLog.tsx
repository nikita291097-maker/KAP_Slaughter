import { useEffect, useState } from 'react';

type EventItem = {
  id: number;
  name: string | null;
  event_class: 'ALARM' | 'DEVIATION' | 'EVENT' | string;
  event_state: 'ACTIVE' | 'CLEARED' | string;
  message: string;
  created_at: string | null;
  cleared_at: string | null;
};

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

export default function EventLog() {
  const [events, setEvents] = useState<EventItem[]>([]);

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

    loadEvents();
    const timerId = window.setInterval(loadEvents, 3000);

    return () => {
      isMounted = false;
      window.clearInterval(timerId);
    };
  }, []);

  return (
    <section className="event-log" aria-label="Журнал событий">
      <h2 className="event-log__title">ЖУРНАЛ СОБЫТИЙ</h2>
      <div className="event-log__table-wrap">
        <table className="event-log__table">
          <thead>
            <tr>
              <th>Время</th>
              <th>Класс</th>
              <th>Описание</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr
                key={event.id}
                className={`event-log__row event-log__row--${event.event_class.toLowerCase()} ${
                  event.event_state === 'ACTIVE' ? 'event-log__row--active' : 'event-log__row--cleared'
                }`}
              >
                <td>{formatDateTime(event.created_at)}</td>
                <td>{event.event_class}</td>
                <td>{event.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
