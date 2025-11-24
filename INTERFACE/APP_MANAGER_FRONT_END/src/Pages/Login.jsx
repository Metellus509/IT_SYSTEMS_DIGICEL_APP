import '../Style/Login.css';
import logo from '../assets/Digicel-Logo-Small.png';

function Login() {
  return (
    <div className="login-wrapper">
      <div className="container-fluid px-1 px-md-5 px-lg-1 px-xl-5 py-5 mx-auto">
        <div className="card card0 border-0">
          <div className="row d-flex">
            <div className="col-lg-6">
              <div className="card1 pb-5">
                <div className="row">
                
                   <img src="" alt="" />
                </div>
                <div className="row px-3 justify-content-center mt-4 mb-5 border-line">
                  <img src="https://i.imgur.com/uNGdWHi.png" className="image" />
                </div>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="card2 card border-0 px-4 py-5">
                <div className="row mb-4 px-3">
                
                </div>
                <div className="row px-3 mb-4">
                  <div className="line" />
                  <small className="or text-center"></small>
                  <div className="line" />
                </div>
                <div className="row px-3">
                  <label className="mb-1"><h6 className="mb-0 text-sm">Email Address</h6></label>
                  <input className="mb-4" type="text" name="email" placeholder="Enter a valid email address" />
                </div>
                <div className="row px-3">
                  <label className="mb-1"><h6 className="mb-0 text-sm">Password</h6></label>
                  <input type="password" name="password" placeholder="Enter password" />
                </div>
                <div className="row px-3 mb-4">
                  <div className="custom-control custom-checkbox custom-control-inline">
                  
                  </div>
                  <a href="#" className="ml-auto mb-0 text-sm"></a>
                </div>
                <div className="row mb-3 px-3">
                  <button type="submit" className="btn btn-blue text-center">Login</button>
                </div>
                <div className="row mb-4 px-3">
                  <small className="font-weight-bold"> <a className="text-danger"></a></small>
                </div>
              </div>
            </div>
          </div>
          <div className="bg-blue py-4">
            <div className="row px-3">
              <small className="ml-4 ml-sm-5 mb-2">Copyright © 2025. All rights reserved - IT Systems Department.</small>
              <div className="social-contact ml-4 ml-sm-auto">
                <span className="fa fa-facebook mr-4 text-sm" />
                <span className="fa fa-google-plus mr-4 text-sm" />
                <span className="fa fa-linkedin mr-4 text-sm" />
                <span className="fa fa-twitter mr-4 mr-sm-5 text-sm" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login;
