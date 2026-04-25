import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

jest.mock('./components/ChatBox', () => function MockChatBox() {
  return <div>Mock Chat</div>;
});

test('renders AutoInsights heading', () => {
  render(<App />);
  const heading = screen.getByText(/AutoInsights/i);
  expect(heading).toBeInTheDocument();
});
