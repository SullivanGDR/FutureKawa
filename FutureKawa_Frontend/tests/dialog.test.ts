import { describe, it, expect } from 'vitest'

/**
 * Tests de la logique du composant UiDialog.vue.
 * Fonctions extraites des computed `dialogTitle` et `confirmBtnStyle`.
 */

type DialogType = 'info' | 'error' | 'success' | 'warning'

function getDialogTitle(type: DialogType, isConfirm: boolean): string {
  if (isConfirm) return 'Confirmation Requise'
  if (type === 'error') return 'Signalement / Erreur'
  if (type === 'success') return 'Opération Réussie'
  if (type === 'warning') return 'Attention / Alerte'
  return 'Message Système'
}

function getConfirmBtnColor(type: DialogType, isConfirm: boolean): string | null {
  if (type === 'error' || isConfirm) return 'danger'
  if (type === 'success') return 'success'
  return null
}

function isConfirmDialog(isConfirm: boolean): boolean {
  return isConfirm
}

describe('UiDialog — titre de la fenêtre', () => {
  it('confirmation override le type', () => {
    expect(getDialogTitle('info', true)).toBe('Confirmation Requise')
  })

  it('confirmation avec type error donne Confirmation Requise', () => {
    expect(getDialogTitle('error', true)).toBe('Confirmation Requise')
  })

  it('type error → Signalement / Erreur', () => {
    expect(getDialogTitle('error', false)).toBe('Signalement / Erreur')
  })

  it('type success → Opération Réussie', () => {
    expect(getDialogTitle('success', false)).toBe('Opération Réussie')
  })

  it('type warning → Attention / Alerte', () => {
    expect(getDialogTitle('warning', false)).toBe('Attention / Alerte')
  })

  it('type info → Message Système', () => {
    expect(getDialogTitle('info', false)).toBe('Message Système')
  })
})

describe('UiDialog — couleur bouton confirmation', () => {
  it('type error → couleur danger', () => {
    expect(getConfirmBtnColor('error', false)).toBe('danger')
  })

  it('isConfirm true → couleur danger (indépendant du type)', () => {
    expect(getConfirmBtnColor('info', true)).toBe('danger')
    expect(getConfirmBtnColor('success', true)).toBe('danger')
  })

  it('type success → couleur success', () => {
    expect(getConfirmBtnColor('success', false)).toBe('success')
  })

  it('type info sans confirm → pas de couleur spéciale', () => {
    expect(getConfirmBtnColor('info', false)).toBeNull()
  })

  it('type warning sans confirm → pas de couleur spéciale', () => {
    expect(getConfirmBtnColor('warning', false)).toBeNull()
  })
})

describe('UiDialog — état confirmation', () => {
  it('isConfirm true active le bouton Annuler', () => {
    expect(isConfirmDialog(true)).toBe(true)
  })

  it('isConfirm false = alerte simple, pas de bouton Annuler', () => {
    expect(isConfirmDialog(false)).toBe(false)
  })
})
