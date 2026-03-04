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
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reference Models</h1>
          <p className="text-gray-600 mt-1">Browse and search architecture reference models</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          Add Model
        </button>
      </div>

      {/* Search Bar */}
      <div className="flex gap-2 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search models semantically (e.g., 'carbon tracking', 'supply chain')..."
            className="w-full pl-10 pr-10 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {searchQuery && (
            <button
              onClick={handleClearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-colors"
        >
          {isSearching ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
        </button>
      </div>

      {/* Results Info */}
      {searchResults !== null && (
        <div className="mb-4 text-sm text-gray-600">
          Found {searchResults.length} results for "{searchQuery}"
          <button onClick={handleClearSearch} className="ml-2 text-blue-600 hover:underline">
            Clear search
          </button>
        </div>
      )}

      {/* Models Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading models...</div>
      ) : displayModels.length === 0 ? (
        <div className="text-center py-12">
          <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">
            {searchResults !== null ? 'No models found for your search.' : 'No reference models yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {displayModels.map(model => (
            <div
              key={model.id}
              className="bg-white rounded-lg p-5 shadow-sm border hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Database className="w-5 h-5 text-purple-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 truncate">{model.name}</h3>
                    {model.score !== undefined && (
                      <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
                        {Math.round(model.score * 100)}% match
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{model.description}</p>
                  {model.tags?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {model.tags.map(tag => (
                        <span
                          key={tag}
                          className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded"
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Add Reference Model</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g., PCF Exchange"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Describe the reference model..."
                  rows={3}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={newTags}
                  onChange={(e) => setNewTags(e.target.value)}
                  placeholder="e.g., carbon, sustainability, catena-x"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddModel}
                disabled={!newName.trim() || !newDescription.trim() || isAdding}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
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
