import './Layout.css'

function Layout({ children }) {
  return (
    <div className="layout">
      <div className="layout-content">{children}</div>
      <footer className="app-footer">
        Created by Iliya Ruvinsky and Codex
      </footer>
    </div>
  )
}

export default Layout

