import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import {MainForm, NavForm} from './main';
import { SignupForm, LoginForm, LogoutForm, FindIDForm, FindPWForm, ResetPWForm, SettingForm, SignupRedirect } from './account';
import { ProfileForm } from './profile';
import { ChatForm, DMForm, TestForm } from './chat';
import { FriendListForm } from './friend';
import { NotFoundForm, FooterForm, PrepareForm, Policy } from './snippets';
import { CMainForm, CCreateForm, CDetailForm } from './community';
import { E1I5Stream } from './e1i5';

import { UserProvider } from './UserContext';

function App() {
  return (
    <UserProvider>
        <Router>
            <div className="App">
                <NavForm />
                <Routes>
                    <Route path="/" element={<MainForm />} />
                    <Route path="/signup" element={<SignupForm />} />
                    <Route path="/login" element={<LoginForm />} />
                    <Route path="/logout" element={<LogoutForm />} />
                    <Route path="/chat" element={<ChatForm />} />
                    <Route path="/profile" element={<ProfileForm />} />
                    <Route path="/friend" element={<FriendListForm />} />
                    <Route path="/dm/:id" element={<DMForm />} />
                    <Route path="/find-id" element={<FindIDForm />} />
                    <Route path="/find-pw" element={<FindPWForm />} />
                    <Route path="/password-reset/:uidb64/:token" element={<ResetPWForm />} />
                    <Route path="/password-change" element={<ResetPWForm />} />
                    <Route path="/setting" element={<SettingForm />} />
                    <Route path="/activate/:uidb64/:token" element={<SignupRedirect />} />
                    <Route path="/community" element={<CMainForm />} />
                    {/*<Route path="/community" element={<PrepareForm />} />*/}
                    <Route path="/community/create" element={<CCreateForm />} />
                    <Route path="/community/posts/:pk" element={<CDetailForm />} />
                    <Route path="/policy" element={<Policy />} />
                    {/*<Route path="/test" element={<TestForm />} />*/}
                    <Route path="/admin" element={<MainForm />} />
                    {/*<Route path="/e1i5" element={<E1I5Stream />} />*/}
                    <Route path="*" element={<NotFoundForm />} />
                </Routes>
                <FooterForm />
            </div>
        </Router>
    </UserProvider>
  );
}

export default App;