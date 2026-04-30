import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import CaseListView from '../../src/views/CaseListView.vue'

describe('CaseListView', () => {
  it('renders case list title', () => {
    const wrapper = mount(CaseListView, {
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key: string) => key,
        },
      },
    })
    expect(wrapper.find('h1').text()).toContain('cases.title')
  })

  it('displays create case button', () => {
    const wrapper = mount(CaseListView, {
      global: {
        plugins: [createPinia()],
        mocks: {
          $t: (key: string) => key,
        },
      },
    })
    expect(wrapper.find('button').text()).toContain('cases.create')
  })
})
