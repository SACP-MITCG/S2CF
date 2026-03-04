import { useEffect, useState, useCallback } from 'react'
import { Database, Plus, Search, X, Loader2, Tag } from 'lucide-react'
import { fetchModels, addModel, searchModels, type ReferenceModel } from '../lib/api'

export default function Models() {
  const [models, setModels] = useState<ReferenceModel[]>([])
  const [searchResults, setSearchResults] = useState<ReferenceModel[] | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)

  // Add model form state
  const [newName, setNewName] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [newTags, setNewTags] = useState('')
  const [isAdding, setIsAdding] = useState(false)

  const loadModels = useCallback(async () => {
    try {
      const data = await fetchModels()
      setModels(data)
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadModels()
  }, [loadModels])

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults(null)
      return
    }

    setIsSearching(true)
    try {
      const result = await searchModels(searchQuery)
      setSearchResults(result.results)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setIsSearching(false)
    }
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setSearchResults(null)
  }

  const handleAddModel = async () => {
    if (!newName.trim() || !newDescription.trim()) return

    setIsAdding(true)
    try {
      await addModel(
        newName.trim(),
        newDescription.trim(),
        newTags.split(',').map(t => t.trim()).filter(Boolean)
      )
      setShowAddModal(false)
      setNewName('')
      setNewDescription('')
      setNewTags('')
      await loadModels()
    } catch (error) {
      console.error('Failed to add model:', error)
      alert('Failed to add model. Please try again.')
    } finally {
      setIsAdding(false)
    }
  }

  const displayModels = searchResults !== null ? searchResults : models

  return (
    <div className="p-8 overflow-auto">
      <div className="flex items-center justify-between mb-8 animate-fade-in">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Reference Models</h1>
          <p className="text-muted-foreground mt-1">Browse and search architecture reference models</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary"
        >
          <Plus className="w-5 h-5" />
          Add Model
        </button>
      </div>

      {/* Search Bar */}
      <div className="flex gap-2 mb-6 animate-fade-in stagger-1">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search models semantically (e.g., 'carbon tracking', 'supply chain')..."
            className="input-editorial pl-10 pr-10"
          />
          {searchQuery && (
            <button
              onClick={handleClearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="btn-secondary disabled:opacity-50"
        >
          {isSearching ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
        </button>
      </div>

      {/* Results Info */}
      {searchResults !== null && (
        <div className="mb-4 text-sm text-muted-foreground">
          Found {searchResults.length} results for "{searchQuery}"
          <button onClick={handleClearSearch} className="ml-2 text-primary hover:underline">
            Clear search
          </button>
        </div>
      )}

      {/* Models Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">Loading models...</div>
      ) : displayModels.length === 0 ? (
        <div className="text-center py-12 animate-fade-in">
          <Database className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
          <p className="text-muted-foreground">
            {searchResults !== null ? 'No models found for your search.' : 'No reference models yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {displayModels.map((model, idx) => (
            <div
              key={model.id}
              className={`card-editorial p-5 animate-fade-in stagger-${Math.min(idx + 1, 5)}`}
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-purple-100 rounded-sm">
                  <Database className="w-5 h-5 text-purple-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-foreground truncate">{model.name}</h3>
                    {model.score !== undefined && (
                      <span className="badge-status badge-approved">
                        {Math.round(model.score * 100)}% match
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{model.description}</p>
                  {model.tags?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {model.tags.map(tag => (
                        <span
                          key={tag}
                          className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-muted text-muted-foreground rounded-sm"
                        >
                          <Tag className="w-3 h-3" />
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Model Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-foreground/50 flex items-center justify-center z-50">
          <div className="card-editorial p-6 w-full max-w-md animate-fade-in">
            <h2 className="text-xl font-semibold text-foreground mb-4">Add Reference Model</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g., PCF Exchange"
                  className="input-editorial"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Description</label>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Describe the reference model..."
                  rows={3}
                  className="input-editorial"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={newTags}
                  onChange={(e) => setNewTags(e.target.value)}
                  placeholder="e.g., carbon, sustainability, catena-x"
                  className="input-editorial"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="btn-ghost"
              >
                Cancel
              </button>
              <button
                onClick={handleAddModel}
                disabled={!newName.trim() || !newDescription.trim() || isAdding}
                className="btn-primary disabled:opacity-50"
              >
                {isAdding ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Add Model'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
