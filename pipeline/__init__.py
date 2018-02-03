from processor import ContentProcessor
from processor.insert_seo_content import InsertSeoContentProcessor


class Pipeline:

    def __init__(self, processors=None):
        if not processors:
            self._processors = [ContentProcessor()]
        else:
            self._processors = processors

    def __len__(self):
        return len(self._processors)

    def __getitem__(self, position):
        return self._processors[position]

    def __setitem__(self, position, processor):
        self._processors[position]= processor

    def append_processor(self, processor):
        self._processors.append(processor)

    def __repr__(self):
        return str(self._processors)

    def execute(self, source_text):
        result = source_text
        for processor in self._processors:
            result = processor.process(result)
        return result

if __name__ == "__main__":
    import os
    count=0
    pipeline = Pipeline([InsertSeoContentProcessor()])
    for dirpath, dirs, files in os.walk("/Users/dbansal/Work/MyCode/wp-auto-poster/posts"):
        for filename in files:
            if filename not in ['metadata.json'] \
                    and not filename.lower().endswith(".jpg")\
                    and not filename.endswith(".DS_Store"):
                source_file = os.path.join(dirpath, filename)
                with open(source_file, 'r') as f:
                    target_text = pipeline.execute(f.read())
                with open(source_file, 'w') as f:
                    print "Writing file {}".format(source_file)
                    f.write(target_text)


