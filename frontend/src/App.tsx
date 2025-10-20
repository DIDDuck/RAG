import "./App.css";
import { useState } from "react";
import { backendUrl, development } from "../config.ts";
import Markdown from "react-markdown";

const RAGForm = () => {

	const [showAnswer, setShowAnswer] = useState(false);
	const [showError, setShowError] = useState(false);
	const [error, setError] = useState(""); 
	const [answer, setAnswer] = useState("");
	const [message, setMessage] = useState("");

	const sendForm = async (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		setError("");
		setShowError(false);
		setAnswer("");
		setShowAnswer(false);

		const sendData = {
			message: event.currentTarget.message.value
		}; 

		try {
			const response = await fetch(backendUrl, {
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
			
		} catch(error) {
			if (development) console.log("Error in getting response from backend:", error);
			setError("Failed to get response.")
			setShowError(true);
		} 
	};

	return (
			<div className="mx-auto max-w-2xl p-4 bg-zinc-900 border border-gray-400 rounded">
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
					{showAnswer && <div>
						<p className="mb-1">Answer:</p>
						<div id="answerDiv" className="mb-2 p-2 w-full border border-gray-400 bg-zinc-800 rounded whitespace-pre-line">
							<Markdown>{answer}</Markdown>
						</div>
					</div>}
					{showError && <div className="mb-2 p-2 w-full border border-gray-500 rounded">
						<p className="text-red-500">{error}</p>
					</div>}
					<button type="submit" className="block mr-auto mt-3 p-1 px-2 bg-amber-400 text-zinc-950 opacity-75 border border-gray-500 rounded">Send</button>
				</form>
			</div>
	)
}

export default RAGForm
