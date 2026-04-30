import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import CaseDetailView from '../../src/views/CaseDetailView.vue'

describe('CaseDetailView', () => {
  beforeEach(() => {
    // Reset state before each test
  })

  it('renders case detail header', () => {
    const wrapper = mount(CaseDetailView, {
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key: string) => key,
          $route: { params: { id: 'test-case-id' } },
          $router: { push: () => {} },
        },
      },
    })
    expect(wrapper.find('.case-detail-view').exists()).toBe(true)
  })

  it('displays pipeline stages', () => {
    const wrapper = mount(CaseDetailView, {
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key: string) => key,
          $route: { params: { id: 'test-case-id' } },
          $router: { push: () => {} },
        },
      },
    })
    expect(wrapper.find('.stage-navigation').exists()).toBe(true)
  })
})
