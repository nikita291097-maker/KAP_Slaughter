import { useEffect, useState } from 'react';

import Conveyor, { type ConveyorStatus } from './Conveyor';

type ConveyorData = {
  id: number;
  name: string;
  status: ConveyorStatus;
  carcass_count: number;
  updated_at: string | null;
};

export default function ConveyorList() {
  const [conveyors, setConveyors] = useState<ConveyorData[]>([]);

  useEffect(() => {
    let isMounted = true;

    const loadConveyors = async () => {
      try {
        const response = await fetch('/api/conveyors');
        if (!response.ok) {
          return;
        }

        const data = (await response.json()) as ConveyorData[];
        if (isMounted) {
          setConveyors(data);
        }
      } catch (_error) {
        // noop
      }
    };

    loadConveyors();
    const timerId = window.setInterval(loadConveyors, 10000);

    return () => {
      isMounted = false;
      window.clearInterval(timerId);
    };
  }, []);

  return (
    <section className="conveyor-list" aria-label="Мнемосхема конвейеров">
      {conveyors.map((conveyor) => (
        <Conveyor
          key={conveyor.id}
          name={conveyor.name}
          status={conveyor.status}
          carcassCount={conveyor.carcass_count}
          updatedAt={conveyor.updated_at}
        />
      ))}
    </section>
  );
}
