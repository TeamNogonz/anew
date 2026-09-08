import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi, test, expect } from 'vitest';
import Home from './pages/Home';
import ApiService from './api/services';
vi.mock('./api/services', () => ({ default: { getNewsData: vi.fn() } }));

test('empty news is a meaningful empty state', async () => {
  ApiService.getNewsData.mockResolvedValue({summary_items: []});
  render(<Home />);
  expect(await screen.findByText(/아직 AI로 요약된 뉴스가 없어요/)).toBeInTheDocument();
});

test('storage failure is not presented as empty news', async () => {
  ApiService.getNewsData.mockRejectedValue(new Error('offline'));
  render(<Home />);
  expect(await screen.findByText('데이터를 불러오지 못했습니다.')).toBeInTheDocument();
});
