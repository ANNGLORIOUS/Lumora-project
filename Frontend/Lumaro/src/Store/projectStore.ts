import { create } from 'zustand'
import type { Project } from '../types'

type ProjectState = {
  projects: Project[]
  setProjects: (p: Project[]) => void
}

export const useProjectStore = create<ProjectState>((set: (partial: Partial<ProjectState>) => void) => ({
  projects: [],
  setProjects: (projects: Project[]) => set({ projects }),
}))
