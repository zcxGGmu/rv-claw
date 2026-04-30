import { ref, onUnmounted } from 'vue'
import type { AgentEvent } from '@/types/event'
import { subscribeCaseEvents } from '@/api/cases'

export interface UseCaseEventsOptions {
  onStageChange?: (stage: string, status: string) => void
  onAgentOutput?: (type: string, content: string) => void
  onReviewRequest?: (stage: string, artifactRef: string) => void
  onIterationUpdate?: (iteration: number) => void
  onCostUpdate?: (cost: number) => void
  onError?: (message: string) => void
  onCompleted?: () => void
}

export function useCaseEvents(caseId: string, options: UseCaseEventsOptions = {}) {
  const isConnected = ref(false)
  const lastError = ref<string | null>(null)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  let unsubscribe: (() => void) | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const connect = () => {
    if (unsubscribe) {
      unsubscribe()
    }

    try {
      unsubscribe = subscribeCaseEvents(caseId, {
        onStageChange: (stage, status) => {
          isConnected.value = true
          lastError.value = null
          options.onStageChange?.(stage, status)
        },
        onAgentOutput: (type, content) => {
          options.onAgentOutput?.(type, content)
        },
        onReviewRequest: (stage, artifactRef) => {
          options.onReviewRequest?.(stage, artifactRef)
        },
        onIterationUpdate: (iteration) => {
          options.onIterationUpdate?.(iteration)
        },
        onCostUpdate: (cost) => {
          options.onCostUpdate?.(cost)
        },
        onError: (message) => {
          lastError.value = message
          options.onError?.(message)
          attemptReconnect()
        },
        onCompleted: () => {
          options.onCompleted?.()
        },
      })

      isConnected.value = true
      lastError.value = null
      reconnectAttempts.value = 0
    } catch (error) {
      lastError.value = 'Failed to connect to event stream'
      attemptReconnect()
    }
  }

  const attemptReconnect = () => {
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      lastError.value = 'Max reconnection attempts reached'
      return
    }

    reconnectAttempts.value++
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)

    reconnectTimer = setTimeout(() => {
      connect()
    }, delay)
  }

  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (unsubscribe) {
      unsubscribe()
      unsubscribe = null
    }
    isConnected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    lastError,
    reconnectAttempts,
    connect,
    disconnect,
  }
}
