// Utility function to safely extract error messages from API responses
export const extractErrorMessage = (error: any): string => {
  // Handle different error formats
  if (typeof error === 'string') {
    return error
  }
  
  if (error && typeof error === 'object') {
    // Pydantic validation error format (422 errors)
    if (Array.isArray(error) && error.length > 0) {
      const firstError = error[0]
      if (firstError && typeof firstError === 'object') {
        if (firstError.msg) {
          return firstError.msg
        }
        if (firstError.message) {
          return firstError.message
        }
        // For validation errors, provide a more user-friendly message
        if (firstError.type && firstError.loc) {
          return `Invalid ${firstError.loc.join('.')}: ${firstError.msg || 'Please check your input'}`
        }
      }
      return String(error[0])
    }
    
    // Standard error object
    if (error.message) {
      return typeof error.message === 'string' ? error.message : JSON.stringify(error.message)
    }
    
    // Detail field (common in FastAPI)
    if (error.detail) {
      if (typeof error.detail === 'string') {
        return error.detail
      }
      if (Array.isArray(error.detail)) {
        return extractErrorMessage(error.detail)
      }
      return JSON.stringify(error.detail)
    }
    
    // Error field
    if (error.error) {
      return typeof error.error === 'string' ? error.error : JSON.stringify(error.error)
    }
    
    // For objects with type, loc, msg, input (Pydantic validation errors)
    if (error.type && error.msg) {
      return error.msg
    }
    
    // Last resort - stringify the object but make it readable
    try {
      return JSON.stringify(error, null, 2)
    } catch {
      return String(error)
    }
  }
  
  return 'An unknown error occurred'
}

// Utility to safely render any value as a string
export const safeRender = (value: any, fallback: string = ''): string => {
  if (value === null || value === undefined) {
    return fallback
  }
  
  if (typeof value === 'string') {
    return value
  }
  
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }
  
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  
  return String(value)
}