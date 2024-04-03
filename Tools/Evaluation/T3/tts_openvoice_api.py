from gradio_client import Client

client = Client("https://myshell-ai-openvoice.hf.space/--replicas/grfvo/")
result = client.predict(
		"He hoped there would be stew for dinner, turnips and carrots and bruised potatoes and fat mutton pieces to be ladled out in thick, peppered, flour-fattened sauce.",	# str  in 'Text Prompt' Textbox component
		"default",	# str (Option from: [('default', 'default'), ('whispering', 'whispering'), ('cheerful', 'cheerful'), ('terrified', 'terrified'), ('angry', 'angry'), ('sad', 'sad'), ('friendly', 'friendly')]) in 'Style' Dropdown component
		"C:/Users/echriston/Documents/stage_2024_nao/speaker2.mp3",	# str (filepath on your computer (or URL) of file) in 'Reference Audio' Audio component
		True,	# bool  in 'Agree' Checkbox component
		fn_index=1
)
print(result)