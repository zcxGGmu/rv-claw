import { describe, it, expect } from 'vitest'
import { useCaseEvents } from '../../src/composables/useCaseEvents'

describe('useCaseEvents', () => {
  it('initializes with disconnected state', () => {
    const { isConnected } = useCaseEvents('test-case-id')
    expect(isConnected.value).toBe(false)
  })

  it('tracks reconnection attempts', () => {
    const { reconnectAttempts } = useCaseEvents('test-case-id')
    expect(reconnectAttempts.value).toBe(0)
  })
})
