
function Card(){
     const servers = [
    { id: 1, name: 'Server 1', location: 'New York', type: 'Production', password: 'pass123' },
    { id: 2, name: 'Server 2', location: 'London', type: 'Staging', password: 'secret456' },
    { id: 3, name: 'Server 3', location: 'Tokyo', type: 'Development', password: 'dev789' },
    { id: 4, name: 'Server 1', location: 'New York', type: 'Production', password: 'pass123' },
    { id: 5, name: 'Server 2', location: 'London', type: 'Staging', password: 'secret456' },
    { id: 6, name: 'Server 3', location: 'Tokyo', type: 'Development', password: 'dev789' },
    { id: 7, name: 'Server 1', location: 'New York', type: 'Production', password: 'pass123' },
    { id: 8, name: 'Server 2', location: 'London', type: 'Staging', password: 'secret456' },
    { id: 9, name: 'Server 3', location: 'Tokyo', type: 'Development', password: 'dev789' },
    { id: 10, name: 'Server 3', location: 'Tokyo', type: 'Development', password: 'dev789' },
  ];

    return <>
         <div className="container my-5">
      <div className="card shadow w-80">
        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">Liste des serveurs</h5>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped table-hover">
              <thead className="table-dark">
                <tr>
                  <th>ID</th>
                  <th>Server Name</th>
                  <th>Location</th>
                  <th>Type</th>
                  <th>Password</th>
                </tr>
              </thead>
              <tbody>
                {servers.map((server) => (
                  <tr key={server.id}>
                    <td>{server.id}</td>
                    <td>{server.name}</td>
                    <td>{server.location}</td>
                    <td>{server.type}</td>
                    <td>{server.password}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    </>
}
export default Card