/**
 * Lightweight toast utility.
 * Any component can call toast('Message') without prop drilling or context.
 * ToastContainer in App.jsx listens for the custom event and renders it.
 *
 * Usage:
 *   import { toast } from '../utils/toast.js'
 *   toast('Reflection saved')
 *   toast('Something went wrong', 'error')
 */

export function toast(message, type = 'success') {
  window.dispatchEvent(
    new CustomEvent('app:toast', { detail: { message, type, id: Date.now() } })
  )
}
