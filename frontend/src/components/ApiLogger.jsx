import { useEffect, useState } from 'react'
import { subscribeApiLogs } from '../api/client'

export default function ApiLogger() {
  const [logs, setLogs] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const [selectedLog, setSelectedLog] = useState(null)

  useEffect(() => {
    const unsubscribe = subscribeApiLogs((newLog) => {
      setLogs((prev) => [newLog, ...prev.slice(0, 49)]) // Giữ tối đa 50 logs gần nhất
    })
    return unsubscribe
  }, [])

  return (
    <div className="card" style={{ marginTop: 24 }}>
      <div className="card-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          📡 Nhật Ký Gọi API Backend Trực Tiếp (Live HTTP Logger)
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            ({logs.length} requests)
          </span>
        </span>
        <div style={{ display: 'flex', gap: 8 }}>
          {logs.length > 0 && (
            <button className="btn btn-sm btn-outline" onClick={() => setLogs([])}>
              Xóa Logs
            </button>
          )}
          <button
            className="btn btn-sm btn-secondary"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? 'Thu gọn ▲' : 'Mở rộng xem chi tiết ▼'}
          </button>
        </div>
      </div>

      {logs.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Chưa có request nào được gửi. Hãy thử thực hiện một thao tác trên giao diện.
        </p>
      ) : (
        <div>
          <div className="logger-card">
            {logs.slice(0, isOpen ? 20 : 4).map((log) => {
              const statusClass =
                log.status === 200 || log.status === 201 || log.status === 204
                  ? 's-200'
                  : log.status === 400 || log.status === 422
                  ? 's-400'
                  : 's-401'

              return (
                <div
                  key={log.id}
                  className="log-item"
                  style={{ cursor: 'pointer' }}
                  onClick={() => setSelectedLog(log)}
                  title="Bấm để xem chi tiết Request/Response"
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span className={`log-status ${statusClass}`}>{log.status}</span>
                    <strong style={{ color: '#60a5fa' }}>{log.method}</strong>
                    <span style={{ color: 'var(--text-main)' }}>{log.url}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-muted)' }}>
                    <span>{log.durationMs}ms</span>
                    <span>{log.timestamp}</span>
                  </div>
                </div>
              )
            })}
          </div>

          {selectedLog && (
            <div className="modal-overlay">
              <div className="modal" style={{ maxWidth: 650 }}>
                <div className="modal-header">
                  <h3>🔍 Chi Tiết Request #{selectedLog.id}</h3>
                  <button className="modal-close" onClick={() => setSelectedLog(null)}>✕</button>
                </div>
                <div style={{ fontSize: '0.85rem' }}>
                  <p><strong>Endpoint:</strong> <code>{selectedLog.method} {selectedLog.url}</code></p>
                  <p><strong>Status:</strong> {selectedLog.status} ({selectedLog.durationMs}ms)</p>

                  <div style={{ marginTop: 12 }}>
                    <strong>Request Payload:</strong>
                    <pre style={{ background: '#020617', padding: 10, borderRadius: 6, overflowX: 'auto', marginTop: 4 }}>
                      {selectedLog.requestBody ? JSON.stringify(selectedLog.requestBody, null, 2) : 'null (None)'}
                    </pre>
                  </div>

                  <div style={{ marginTop: 12 }}>
                    <strong>Response Data:</strong>
                    <pre style={{ background: '#020617', padding: 10, borderRadius: 6, overflowX: 'auto', marginTop: 4, maxHeight: 200 }}>
                      {selectedLog.responseBody ? JSON.stringify(selectedLog.responseBody, null, 2) : 'null (No Content)'}
                    </pre>
                  </div>
                </div>
                <div className="modal-footer">
                  <button className="btn btn-primary btn-sm" onClick={() => setSelectedLog(null)}>
                    Đóng
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
