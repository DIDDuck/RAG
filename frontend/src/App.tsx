import "./App.css";
import { useEffect, useState } from "react";
import { backendChatUrl, development, backendFileListUrl } from "../config.ts";
import Markdown from "react-markdown";

const RAGForm = () => {

	const [showAnswer, setShowAnswer] = useState(false);
	const [showError, setShowError] = useState(false);
	const [error, setError] = useState(""); 
	const [answer, setAnswer] = useState("");
	const [message, setMessage] = useState("");
	const [fileList, setFileList] = useState<string[]>([]);
	let fileListLoaded = false;

	const sendForm = async (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		setError("");
		setShowError(false);
		setAnswer("");
		setShowAnswer(false);

		const sendData = {
			message: event.currentTarget.message.value,
			file: !event.currentTarget.file ? null : event.currentTarget.file.value
		}; 

		try {
			const response = await fetch(backendChatUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify(sendData)
			})
			if (!response.ok) {
				throw new Error("Bad response from backend.");
			}
			const data = await response.json();
			if (data.error) {
				throw new Error(data.message);
			} else {
				setAnswer(data.text);
				setShowAnswer(true);
			} 
			
		} catch(error: any) {
			if (development) console.log("Error in getting response from backend:", error);
			console.log(error);
			if (error.message === "No files available.") {
				setError("Upload a file to server.")	
			} else setError("Failed to get response.")
			setShowError(true);
		} 
	};

	const getFileList = async () => {
		try {
			const response = await fetch(backendFileListUrl);
			if (!response.ok) throw new Error("Bad response from backend.");
			const data = await response.json();
			if (development) console.log("FILES:", data.files);
			setFileList(data.files);
		} catch(error) {
			if (development) console.log("Error in getting response from backend:", error);
			setError("Failed to get response.")
			setShowError(true);	
		}
	};
	
	useEffect(() => {
		if (fileListLoaded === false) {
			getFileList();
			fileListLoaded = true;
		}	
	}, []);

	return (
			<div className="mx-auto max-w-2xl p-4 overflow-y-auto min-h-screen max-h-screen sm:min-h-auto sm:max-h-screen bg-zinc-900 border border-gray-400 rounded">
				<h1 className="text-center mb-6">Unnamed RAG App</h1>
				<form onSubmit={sendForm}>
					<div className="mb-3 flex flex-col">
						<label htmlFor="message" className="mb-1">Enter your message:</label>
						<textarea 
							id="message" 
							name="message" 
							className="p-2 w-full border border-gray-500 bg-zinc-800 rounded" 
							rows={5}
							value={message}
							onChange={(e)=> setMessage(e.target.value)}></textarea>
					</div>
					<button type="submit" className="block mr-auto mb-3 p-1 px-2 bg-amber-400 text-zinc-950 opacity-75 border border-gray-500 rounded">Send</button>
					{/*<button type="button" className="block mr-auto mb-3 p-1 px-2 bg-amber-400 text-zinc-950 opacity-75 border border-gray-500 rounded" onClick={() => getFileList()}>Show Files</button>*/}
					<div className="mb-5">
						<ul className="list-none">
						{fileList.length !== 0 
							? 
							<div><p className="mb-1">Files available:</p>
								{fileList.map(name => 
									<div key={name} className="flex gap-3"><input type="radio" name="file" value={name} defaultChecked={name === fileList[0] ? true : false} /><li>{name} </li></div>
							)}</div> 
							: <p>No files available.</p>}
						</ul>	
					</div>
					{showAnswer && <div>
						<p className="mb-1">Answer:</p>
						<div id="answerDiv" className="mb-2 p-2 w-full border border-gray-400 bg-zinc-800 rounded whitespace-pre-line">
							<Markdown>{answer}</Markdown>
						</div>
					</div>}
					{showError && <div className="mb-2 p-2 w-full border border-gray-500 rounded">
						<p className="text-red-500">{error}</p>
					</div>}
					
				</form>
			</div>
	)
}

export default RAGForm
