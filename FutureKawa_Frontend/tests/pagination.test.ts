import { describe, it, expect } from 'vitest'

/**
 * Tests de l'algorithme de pagination de UiPagination.vue.
 * Logique extraite du computed `visiblePages`.
 */
function getVisiblePages(currentPage: number, totalPages: number): (number | string)[] {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, i) => i + 1)
  }
  if (currentPage <= 4) {
    return [1, 2, 3, 4, 5, '...', totalPages]
  }
  if (currentPage >= totalPages - 3) {
    return [1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages]
  }
  return [1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages]
}

function getTotalPages(totalItems: number, itemsPerPage: number): number {
  return Math.max(1, Math.ceil(totalItems / itemsPerPage))
}

describe('Pagination — visiblePages', () => {
  it('affiche toutes les pages si total <= 7', () => {
    expect(getVisiblePages(1, 5)).toEqual([1, 2, 3, 4, 5])
  })

  it('affiche toutes les pages si total == 7', () => {
    expect(getVisiblePages(4, 7)).toEqual([1, 2, 3, 4, 5, 6, 7])
  })

  it('affiche début + ellipse si page <= 4 sur 20', () => {
    expect(getVisiblePages(2, 20)).toEqual([1, 2, 3, 4, 5, '...', 20])
  })

  it('affiche fin + ellipse si page proche de la fin (page 18 sur 20)', () => {
    expect(getVisiblePages(18, 20)).toEqual([1, '...', 16, 17, 18, 19, 20])
  })

  it('affiche ellipses des deux côtés pour une page centrale (page 10 sur 20)', () => {
    expect(getVisiblePages(10, 20)).toEqual([1, '...', 9, 10, 11, '...', 20])
  })

  it('page 1 sur 20 — début avec ellipse', () => {
    expect(getVisiblePages(1, 20)).toEqual([1, 2, 3, 4, 5, '...', 20])
  })

  it('dernière page sur 20 — fin avec ellipse', () => {
    expect(getVisiblePages(20, 20)).toEqual([1, '...', 16, 17, 18, 19, 20])
  })

  it('une seule page retourne [1]', () => {
    expect(getVisiblePages(1, 1)).toEqual([1])
  })
})

describe('Pagination — calcul totalPages', () => {
  it('10 éléments / 10 par page = 1 page', () => {
    expect(getTotalPages(10, 10)).toBe(1)
  })

  it('11 éléments / 10 par page = 2 pages', () => {
    expect(getTotalPages(11, 10)).toBe(2)
  })

  it('0 éléments = minimum 1 page', () => {
    expect(getTotalPages(0, 10)).toBe(1)
  })

  it('100 éléments / 10 par page = 10 pages', () => {
    expect(getTotalPages(100, 10)).toBe(10)
  })

  it('101 éléments / 10 par page = 11 pages', () => {
    expect(getTotalPages(101, 10)).toBe(11)
  })
})
