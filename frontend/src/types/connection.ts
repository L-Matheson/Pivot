export interface ConnectionStub {
  id: string
  provider: string
  label: string
  status: 'connected' | 'expired' | 'error'
}
