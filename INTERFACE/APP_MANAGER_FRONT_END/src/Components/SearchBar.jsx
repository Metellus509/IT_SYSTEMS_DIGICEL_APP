import '../Style/SearchBar.css'


function SearchBar(){
    return <>
        <div className='my-5'>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet" />
        <div className="container">
            <div className="row justify-content-center">
            <div className="col-md-6">
                <div className="search-container">
                <input type="text" className="form-control search-input" placeholder="Search..." />
                <i className="fas fa-search search-icon" />
                </div>
            </div>
            </div>
        </div>
        </div>

    </>
}
export default SearchBar;