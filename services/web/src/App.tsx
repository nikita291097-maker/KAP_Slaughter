import Header from './components/Header';
import ConveyorList from './components/ConveyorList';
import EventLog from './components/EventLog';

export default function App() {
  return (
    <main className="scada-screen">
      <Header />
      <ConveyorList />
      <EventLog />
    </main>
  );
}
